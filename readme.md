# 简介

因追番不便，收录各大网站番剧列表，以飨世人[]~(￣▽￣)~*

请访问：[bangumi.feng.zone](http://bangumi.feng.zone)

此外提供 json 接口：`http://bangumi.feng.zone/raw_json` 格式如下：

```json
{  
   "success": 0,
   "data":{  
      "0":[  
         {  
            "url":{  
               "Bilibili":"http://www.bilibili.com/bangumi/i/5523/",
               "Youku":"http://v.youku.com/v_show/id_XMjUxODkwNzM3Mg==.html",
               "iQiyi":"http://www.iqiyi.com/v_19rr9n5c54.html",
               "Tudou":"http://www.tudou.com/albumplay/JA-0VT2hjxY.html"
            },
            "update_time":{  
               "Bilibili":"00:30:00",
               "Youku":"00:30:00",
               "iQiyi":null,
               "Tudou":"00:30:00"
            },
            "weekday":0,
            "title":"3\u6708\u7684\u72ee\u5b50"
         }, //...
     ],
      "1":[
          //...
      ],
      "2":[
          //...
      ],
      "3":[
          //...
      ],
      "4":[
          //...
      ],
      "5":[
          //...
      ],
      "6":[
          //...
      ],
   }
}
```
1. data 的 key 代表星期。1~6 表示周一到周六，0代表周日
2. weekday 代表更新日期，格式同上。
3. success 代表是否成功获取数据，0代表成功。
