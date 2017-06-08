# Chinese Common User Passwords Profiler
基于社会工程学的弱口令密码字典生成工具

# 使用方法 : 
1. 第一步 : 定义已知信息
```
class Person:
    NAME = u"李二狗"
    PHONE = ["13512345678",]
    CARD = "220281198309243953"
    BIRTHDAY = ("1983", "09", "24")
    HOMETOWN = (u"四川", u"成都", u"高新区")
    PLACE = [(u"河北", u"秦皇岛", u"北戴河"),]
    QQ = ["987654321",]
    COMPANY = [(u"腾讯", "tencent"),]
    SCHOOL = [(u"清华大学", u"清华",  "tsinghua")]
    ACCOUNT = ["twodog",]
    PASSWORD = ["old_password",]
```
2. 第二步 : 运行脚本
```
python chinese-weak-password-generator.py
```

# 参考资料
```
http://www.moonsec.com/post-181.html
```
