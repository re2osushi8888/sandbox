# hjq

```
echo '[ { "age": 25, "name": "sato taro", "tel-number": "111-1111" }, { "age": 26, "name": "saito hanako", "tel-number": "222-2222" }, { "age": 27, "name": "yamada taro", "tel-number": "333-3333" } ]' \
| hjq-exe '{"name":.[2].name,"tel-number":.[2].tel-number}'
```
