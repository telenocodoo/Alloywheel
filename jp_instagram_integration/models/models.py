# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import re
import requests
import logging
import base64

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    insta_user = fields.Char(string='Instagram username')
    full_name = fields.Char(string='Name')
    biography = fields.Text(string='Biography')
    external_url = fields.Char(string='External URL')
    followed_by = fields.Integer(string='Followers')
    timeline_media =  fields.Integer(string='Media')
    engagement_rate = fields.Float(string='Engagement Rate')
    engagement_rate_ha = fields.Float(string='Engagement Rate Hype Auditor')
    type_scrape = fields.Selection(string='Type of scrape', selection=[('only', 'Fotos only'), ('both', 'Fotos and Videos'),], default='both')

    def clear_data(self):
            self.full_name = ''
            self.biography = ''
            self.external_url = ''
            self.followed_by = 0
            self.timeline_media = 0
            self.engagement_rate = 0

    def getID(self):
        url = "https://www.instagram.com/{}"

        r = requests.get(url.format(self.insta_user))

        html = r.text

        if r.ok:
            self.clear_data()
            self.full_name = re.findall('"full_name":"(.*?)",', html)[0]
            bio = re.findall('"biography":"(.*?)",', html)[0].replace('\\n', '\n')
            self.biography = bio.encode('utf-16', 'surrogatepass').decode('utf-16')
            eurl = re.findall('"external_url":"(.*?)",', html)
            self.external_url = eurl[0] if len(eurl) else ''
            self.followed_by = re.findall('"edge_followed_by":{"count":(\d+)',html)[0]
            self.timeline_media = re.findall('"edge_owner_to_timeline_media":{"count":(\d+)',html)[0]
            self.image = self.fetch_image_from_url(re.findall('"profile_pic_url_hd":"(.*?)",', html)[0])

            type_graph = re.findall('"__typename":"(.*?)",', html)
            edge_media_to_comment = re.findall('"edge_media_to_comment":{"count":(\d+)',html)
            edge_liked_by = re.findall('"edge_liked_by":{"count":(\d+)',html)

            total_likes = 0
            total_comments = 0
            total_posts = 0

            if self.type_scrape == 'only':
                # Solo para fotos
                for i in range(0,len(edge_liked_by)):
                    if type_graph[i] != 'GraphVideo':
                        total_likes += int(edge_liked_by[i])
                        total_posts += 1
                for i in range(0,len(edge_media_to_comment)):
                    if type_graph[i] != 'GraphVideo':
                        total_comments += int(edge_media_to_comment[i])
                if len(edge_liked_by):
                    self.engagement_rate = ((total_likes + total_comments) / total_posts) / self.followed_by * 100
            else:
                # Fotos y Videos
                for lik in edge_liked_by:
                    total_likes += int(lik)
                for com in edge_media_to_comment:
                    total_comments += int(com)
                if len(edge_liked_by):
                    self.engagement_rate = ((total_likes + total_comments) / len(edge_liked_by)) / self.followed_by * 100

            self.fetchDP(self.insta_user)

        else:
            raise exceptions.ValidationError(
                    _("Invalid username %s" %self.insta_user))

    def fetchDP(self,userID):
        url = "https://app.hypeauditor.com/instagram/{}"

        r = requests.get(url.format(userID))

        if r.status_code == 200:
            result = re.findall('(\d+).(\d+)%',r.text)
            self.engagement_rate_ha = float(result[0][0] + '.' + result[0][1])

    def fetch_image_from_url(self, url):
        data = ''

        try:
            data = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
        except Exception as e:
            _logger.warn('There was a problem requesting the image from URL %s' % url)
            logging.exception(e)

        return data