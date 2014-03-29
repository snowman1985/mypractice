import traceback
from bson.json_util import dumps, loads

def savetotopicdb(filename, tablename, cur):
  with open(filename, 'r') as f:
    for line in f:
      try:
        record = loads(line)
#        print record
        if tablename == "alltable":
          cur.execute(
	  """INSERT INTO  """ + tablename + """ (date, topic_total, topic_android, topic_iphone, topic_web, topic_image, topic_text, comment_day_count, like_count, comment_count) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
               (record['_id'], record['value']['topicCount'], record['value']['androidCount'], record['value']['iphoneCount'], record['value']['webCount'], record['value']['imageCount'], record['value']['textCount'], record['value']['commentDayCount'], record['value']['likea'], record['value']['commentCount']))
        elif tablename == "post_message_statistics":
          cur.execute(
            """INSERT INTO """ + tablename + """ (statistics_date, totality_messages, android, iphone, web, picture_messages, text_messages) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
	       (record['_id'], record['value']['topicCount'], record['value']['androidCount'], record['value']['iphoneCount'], record['value']['webCount'], record['value']['imageCount'], record['value']['textCount']))
        elif tablename == "circle_comment_statistics":
          cur.execute(
	    """INSERT INTO """ + tablename + """ (statistics_date, totality_comments) VALUES (%s, %s)""",
               (record['_id'], record['value']['commentCount']))
        elif tablename == "post_praise_statistics":
          cur.execute(
	    """INSERT INTO """ + tablename + """ (statistics_date, total_like) VALUES (%s, %s)""",
               (record['_id'], record['value']['likea']))
        elif tablename == "im_message_statistics":
          cur.execute(
            """INSERT INTO """ + tablename + """ (statistics_date, android, iphone, web, text_messages, voice_messages, picture_messages) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
               (record['_id'], record['value']['androidCount'], record['value']['iphoneCount'], record['value']['webCount'], record['value']['textCount'], record['value']['audioCount'],
                record['value']['imageCount']))
        elif tablename == "angel_user_circle_statistics":
          cur.execute(
            """INSERT INTO """ + tablename + """ (statistics_date, text_posts, picture_posts, circle_comments, praise_number) VALUES (%s, %s, %s, %s, %s)""",
               (record['_id'], record['value']['textCount'], record['value']['imageCount'], record['value']['commentCount'], record['value']['likea']))
        elif tablename == "feedback_circle_statistics":
          cur.execute(
            """INSERT INTO """ + tablename + """ (statistics_date, text_posts, picture_posts, circle_comments, praise_number) VALUES (%s, %s, %s, %s, %s)""",
               (record['_id'], record['value']['textCount'], record['value']['imageCount'], record['value']['commentCount'], record['value']['likea']))
        elif tablename == "user_login_times_statistics":
          cur.execute(
            """INSERT INTO """ + tablename + """ (statistics_date, android, iphone, web) VALUES (%s, %s, %s, %s)""",
               (record['_id'], record['value'][androidFrom], record['value'][iphoneFrom], record['value']['webFrom']))
      except Exception , e:
        print e
