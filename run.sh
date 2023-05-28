export http_proxy=127.0.0.1:2080
export https_proxy=127.0.0.1:2080
/home/fx/miniconda3/envs/jkfx/bin/python /home/fx/codes/vmess2config/vmess2config.py -u 'link'
sudo cp /home/fx/codes/vmess2config/config.json /usr/local/etc/xray/
sudo cp /home/fx/codes/vmess2config/config.json /usr/local/etc/v2ray/
sudo sed -i 's/1080/1030/' /usr/local/etc/v2ray/config.json
sudo sed -i 's/2080/2030/' /usr/local/etc/v2ray/config.json
/home/fx/codes/vmess2config/fetch_geo.sh
sudo cp /home/fx/codes/vmess2config/geo* /usr/local/share/xray/
sudo cp /home/fx/codes/vmess2config/geo* /usr/local/share/v2ray/
sudo systemctl restart xray
sudo systemctl restart v2ray
