# -*- coding: utf-8 -*-

from facebook import GraphAPI as GraphAPIBase
from facebook import GraphAPIError
from json import loads as _parse_json
import urllib2


token = 'YOUR_ACCESS_TOKEN_HERE'


class GraphAPI(GraphAPIBase):

    def put_photo_comment(self, image, feed_id, message=None, **kwargs):
        """Publish photo comment on feed.
        아나 왜 이걸 안만들어놓은거야 ㅡㅡ
        put_photo에서 소스 가져옴.
        """
        post_args = {
            'access_token': self.access_token,
            'file': image,
            'message': message,
        }
        post_args.update(kwargs)
        content_type, body = self._encode_multipart_form(post_args)
        req = urllib2.Request(("https://graph.facebook.com/%s/comments" %
                               feed_id),
                              data=body)
        req.add_header('Content-Type', content_type)
        try:
            data = urllib2.urlopen(req).read()
        #For Python 3 use this:
        #except urllib2.HTTPError as e:
        except urllib2.HTTPError, e:
            data = e.read()  # Facebook sends OAuth errors as 400, and urllib2
                             # throws an exception, we want a GraphAPIError
        try:
            response = _parse_json(data)
            # Raise an error if we got one, but don't not if Facebook just
            # gave us a Bool value
            if (response and isinstance(response, dict) and
                    response.get("error") and
                    response.get("error")['code'] != 2):
                raise GraphAPIError(response)
        except ValueError:
            response = data

        return response


def troll():
    """ㅋㅋㅋ"""

    # 최근 실행에서 저장된 feed id
    fid = None
    try:
        f = open('fid.txt', 'r')
        fid = f.read().strip()
        f.close()
    except IOError:
        pass
    print '* Last feed id:', fid

    graph = GraphAPI(token)

    print '* Retrieving feeds...',
    feeds = graph.get_connections('shlee322', 'feed',
                                  fields='message,from.id')['data']
    print 'Done'

    if len(feeds):
        print '* Reading image.jpg...',
        img = open('image.jpg')
        print 'Done'

    # 받아온 피드 중 가장 최신 피드의 id
    lastest_feed_id = None
    for feed in feeds:
        # 본인이 직접 작성한 글이 아니면 트롤링 ㄴㄴ
        if 'message' not in feed or feed['from']['id'] != '100001582221312':
            continue

        # feed id가 unicode로 들어와서 encode 해줘야됨
        feed_id = feed['id'].encode('utf-8')

        # 받아온 피드 중 가장 최신의 피드 id 저장
        if lastest_feed_id is None:
            lastest_feed_id = feed_id

        # 최근 실행에서 처리한 피드일 경우 종료
        if fid == feed_id:
            break

        print '* Publishing comment on %s...' % feed_id,
        img.seek(0)
        try:
            graph.put_photo_comment(img, feed_id, message='일 안함? ㅡㅡ')
        except GraphAPIError:
            print 'Failed'
            continue
        print 'Done'

    # 중복검사를 위해 가장 최신 피드 id 저장
    f = open('fid.txt', 'w')
    f.write(lastest_feed_id)
    f.close()
    print '* Finished.'

if __name__ == '__main__':
    troll()
