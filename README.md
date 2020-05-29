# Chinese Common User Passwords Profiler
> 基于社会工程学的弱口令密码字典生成工具

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
> 暂只支持 Python2（依赖库 hanzi2pinyin 暂时没有 Python3 版）

```
python2 chinese-weak-password-generator.py
```
3. 输出生成的密码字典并保存到当前目录 password.list 文件中
```
[+] liergou => de1644a2551503c15176b5b8a5b27c79
[+] Liergou => e4df76f225cae5c0681997967844e094
[+] 13512345678 => 688c96a5bb633ab6ffb491ee6070ac27
[+] 19830924 => 618a337ffb5525156005105b22763ee0
[+] sichuan => 34f280dfd7f86fa505a52836fa8be720
[+] chengdu => 354b500e3a784a489a27ee50d19ba328
[+] gaoxinqu => f4afe70731e17fe24b94badd9d81989a
[+] Sichuan => c01eba257b2d44afb1896051da9185b4
[+] Chengdu => f4aa575f70b3f78887deb96ce611b187
[+] Gaoxinqu => caec347ba4c61605c14699b0d1703d95
[+] qinhuangdao => 34fbdaed690c48b32f07ec44936ade19
[+] beidaihe => 96c9ca76dc81c12f6b1666c6e30004f3
[+] Qinhuangdao => ba302e73c151f9610ca627bf1c843615
[+] Beidaihe => 2bfeb21646a1c54e19491cb8cd7fcaaf
[+] 987654321 => 6ebe76c9fb411be97b3b0d48b791a7c9
[+] tengxun => 9549c286dff3eec9b3bd97ff6c199bde
[+] Tengxun => 06aca03b11b933a52feebad6a70dba9b
[+] tencent => 3da576879001c77b442b9f8ef95c09d6
[+] Tencent => 9414b97199d909061ce91aeb8faa421f
[+] tencent => 3da576879001c77b442b9f8ef95c09d6
[+] qinghuadaxue => 07e3d184643bbb8fc19aabfdc17b5099
[+] Qinghuadaxue => 0d0078ead5f23c6a5a3999d2678bd1b0
[+] qinghua => 21b6fe282fd67514b7dd062ebea60cd6
[+] Qinghua => 124ded788d9d76fee1f505660ab31b97
[+] tsinghua => 552733250c23324e4169dfe43a4b1233
[+] Tsinghua => 6c5c1441e3283e7543342e59277ea219
[+] tsinghua => 552733250c23324e4169dfe43a4b1233
[+] liergou123 => ddd377570e00c707b58fdcabc1284e07
[+] ergou123 => 4565c4b3ff262ec3f36fa3e9236dc2f9
[+] Liergou123 => 37b4b7f76bf5ec4e430e29f97361fc8b
[+] Ergou123 => 24a46328a4b517eb0d19ebe137e19b37
[+] 13512345678123 => 4bede9e906599088b2999de2723daeb3
[+] 5678123 => 76dcf9b102efa543eecc3b9f847e0934
[+] 243953123 => b343b11001bdabf6513ab55ca7cef889
[+] 220281123 => 0ff5d66e1cf72d9280e7c935cd516204
[+] 1983123 => 934cbe84b040cc8f227997c46e50825c
[+] 0924123 => f8993670caaeac3ffec0667b20b6fae2
[+] 19830924123 => 38bda51e49d7dbc9d05f971e708bdc12
[+] sichuan123 => f6a04d5db1b1f61c05dab88c44babdbf
[+] chengdu123 => b0ef8986d2a279db71cc243b45890a41
[+] gaoxinqu123 => bad977ad7ca2ce50b4afe6c286a50f86
[+] Sichuan123 => 46ef84063649179f96719b9e82ab7c38
[+] Chengdu123 => 4eb7c5687a356a473794822a3b607972
[+] Gaoxinqu123 => 6c0700d2452298ba095cca5c625dacf7
[+] hebei123 => 0fd6af13695ce645e421d6b8ecc44afa
[+] qinhuangdao123 => daef90327893a558e061e39deba4c438
[+] beidaihe123 => 36b7699549da7645d34cd680ca119624
[+] Hebei123 => e06e73ddff2b2608f021402b14b24533
[+] Qinhuangdao123 => 5e310dac76c41f794b4dc51ddef8747e
[+] Beidaihe123 => 0d9777ea45400e4984c1a5ddcb01c7f7
[+] 987654321123 => 6932768a2fa35b66643d2b85f8c74f3b
[+] tengxun123 => aaec5c7d699c131f92de802ed0e97b34
[+] Tengxun123 => 1a4341fd6278eb27938275a9ba471942
[+] tencent123 => 7e89ae637d34630951bb16a54eb509ad
[+] Tencent123 => 5c1157efc98a64a758c31f839280dd32
[+] tencent123 => 7e89ae637d34630951bb16a54eb509ad
[+] qinghuadaxue123 => fe9e00002288176cbefc6bccf1ce5070
[+] Qinghuadaxue123 => 5ab2a9cefe356b56cf92b1220b2ebb6a
[+] qhdx123 => c50db9d0b488c010c6fb42b5ff011e57
[+] qinghua123 => 85bfb8827f36a0cdea6bfbc7f1a7e640
[+] Qinghua123 => 6e11028a878522d705a881a58f7e043a
[+] tsinghua123 => 0c07f797cc47f333ea66914e1e942fdc
[+] Tsinghua123 => dd4802e8f366682e64f584a124bca827
[+] tsinghua123 => 0c07f797cc47f333ea66914e1e942fdc
[+] twodog123 => f36bb3069a5dff1e379f6661cfc20510
[+] Twodog123 => cd2c691843e79134a577f4e23529f096
[+] twodog123 => f36bb3069a5dff1e379f6661cfc20510
[+] liergou@ => 15188c6f4ecf8a75afdcc282126a3b63
[+] Liergou@ => ae03dc5278c348d96a630e91b49a23de
[+] 13512345678@ => c73545900759f24b7db46300f667b90e
[+] 243953@ => 210cdf8b221a7d4085dedde2c0eec550
[+] 220281@ => 42c90fae6b332d83727ce281fb4b8b14
[+] 19830924@ => c302c41ecf38bfedf42cccb8c77d9d38
[+] sichuan@ => 195eeb05c2de157df2720a1e0e814f6a
[+] chengdu@ => a6dfb50a2d4fbae87fe599212d99c4ea
[+] gaoxinqu@ => 8b9be9a26915265501e9bc9b283da0bc
[+] Sichuan@ => b7c74335b988bcd0206cc13fb1a01514
[+] Chengdu@ => 02909a156f7a95dfd02f10ce743c3061
[+] Gaoxinqu@ => 5c96d1c46b14c1d1f02854c2f7179471
[+] qinhuangdao@ => 3be6b307e807fb69f2a690169a72d100
[+] beidaihe@ => c678f99cad2d8d7013ef69ad9d42a0d3
[+] Qinhuangdao@ => d6be705e873f2c21cdca9dab7b3d6f64
[+] Beidaihe@ => bc96c22a8276f3025e965b1b1b53d3a0
[+] 987654321@ => 775166f0b8517d632502e5d7415376f8
[+] tengxun@ => 2a1e9a45302a8df38adaec946737ff4c
[+] Tengxun@ => fcc7d393f00907c9bc4e7a63cd8e1d9f
[+] tencent@ => 52163609f75e54ee6fe9c8f76d3e04c0
[+] Tencent@ => 7cb34e3ad7da645ade9621e6fd5cac04
[+] tencent@ => 52163609f75e54ee6fe9c8f76d3e04c0
[+] qinghuadaxue@ => 96d347435f231c802630b058924fdcf4
[+] Qinghuadaxue@ => aa1fafb590a926bdf683a9a12ef49ebb
[+] qinghua@ => 6d1e78889084335a05433b5736cbc6e4
[+] Qinghua@ => 6f668440454daf3e135f9f1faba7d41c
[+] tsinghua@ => c24f6d1e9635faa0a8aa81bfe7f80d57
[+] Tsinghua@ => 9edc7ec2eb0ef43642b3b5af634afe5a
[+] tsinghua@ => c24f6d1e9635faa0a8aa81bfe7f80d57
[+] twodog@ => 13233f59565ca53942d54888be3ecb2c
[+] Twodog@ => 8db63d1f815d2abbe51bf6adbf3a32d9
[+] twodog@ => 13233f59565ca53942d54888be3ecb2c
[+] liergouabc => 754caea1fd5c89c034ea55c0376a7fb9
...
```

# 参考资料

```
http://www.moonsec.com/post-181.html
```
