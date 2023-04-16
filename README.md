## 订阅地址生成 v2ray 负载均衡配置文件

脚本接受订阅地址，生成节点服务器 `outbounds` 列表，并且开启负载均衡。

可以指定默认开启监听的 `socks` 端口和 `http` 端口。

`socks` 默认端口 `1080`， `http` 默认端口 `2080` 。

负载均衡策略为 `leastPing` ，会根据观测记录选择 HTTPS GET 请求完成时间最快的一个出站连接。

> v5 支持了 `leastload` 选项。

### Usage

```sh
usage: vmess2config.py [-h] [-u URL] [-f FILE] [-o OUT] [--socks_port SOCKS_PORT] [--http_port HTTP_PORT]

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     generate v2ray config file from subscribe link
  -f FILE, --file FILE  generate v2ray config file from filesystem
  -o OUT, --out OUT     speifiy generate v2ray config filename
  --socks_port SOCKS_PORT
                        socks inbound port
  --http_port HTTP_PORT
                        http inbound port
```

### Examples

```sh
$> python3 vmess2config.py -u "http://subscribe.link?flag=v2ray"
```

```sh
$> python3 vmess2config.py -f "vmeeses.txt"
```

## 参考文档

- [V2Fly.org](https://www.v2fly.org/config/overview.html)
- [V2Ray 配置指南](https://guide.v2fly.org/)
- [v2rayN](https://github.com/2dust/v2rayN)
- [分享链接格式说明(ver 2)](https://github.com/2dust/v2rayN/wiki/%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5%E6%A0%BC%E5%BC%8F%E8%AF%B4%E6%98%8E(ver-2))
- [Loyalsoldier/v2ray-rules-dat](https://github.com/Loyalsoldier/v2ray-rules-dat)
