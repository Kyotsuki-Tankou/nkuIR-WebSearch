# import wget
# from urllib.parse import quote

# cur_url='https://xb.nankai.edu.cn/upload/20241206092122/%E5%8D%97%E5%8A%9E%E5%8F%91%E3%80%942024%E3%80%9542%E5%8F%B7%E8%BD%AC%E5%8F%91%E7%A0%94%E7%A9%B6%E7%94%9F%E9%99%A2%E3%80%8A%E5%85%B3%E4%BA%8E%E5%85%AC%E5%B8%83%E5%8D%97%E5%BC%80%E5%A4%A7%E5%AD%A62024%E5%B9%B4%E4%BC%98%E7%A7%80%E7%A1%95%E5%A3%AB%E5%AD%A6%E4%BD%8D%E8%AE%BA%E6%96%87%E5%90%8D%E5%8D%95%E5%8F%8A%E8%A1%A8%E5%BD%B0%E6%8C%87%E5%AF%BC%E6%95%99%E5%B8%88%E7%9A%84%E9%80%9A%E7%9F%A5%E3%80%8B.pdf'
# encoded_url = quote(cur_url, safe=':/')

# wget.download(url=encoded_url,out='./pages/南办发〔2024〕41号关于启用“南开大学仪器平台（1）、（2）”印章的通知.pdf')
# import requests

# url = 'https://xb.nankai.edu.cn/upload/20241206092122/%E5%8D%97%E5%8A%9E%E5%8F%91%E3%80%942024%E3%80%9542%E5%8F%B7%E8%BD%AC%E5%8F%91%E7%A0%94%E7%A9%B6%E7%94%9F%E9%99%A2%E3%80%8A%E5%85%B3%E4%BA%8E%E5%85%AC%E5%B8%83%E5%8D%97%E5%BC%80%E5%A4%A7%E5%AD%A62024%E5%B9%B4%E4%BC%98%E7%A7%80%E7%A1%95%E5%A3%AB%E5%AD%A6%E4%BD%8D%E8%AE%BA%E6%96%87%E5%90%8D%E5%8D%95%E5%8F%8A%E8%A1%A8%E5%BD%B0%E6%8C%87%E5%AF%BC%E6%95%99%E5%B8%88%E7%9A%84%E9%80%9A%E7%9F%A5%E3%80%8B.pdf'
# output_path = './pages/南办发〔2024〕41号关于启用“南开大学仪器平台（1）、（2）”印章的通知.pdf'

# response = requests.get(url, stream=True)  # 使用 stream 提高效率
# if response.status_code == 200:
#     with open(output_path, 'wb') as file:
#         for chunk in response.iter_content(chunk_size=8192):  # 分块写入
#             file.write(chunk)
#     print("Download complete!")
# else:
#     print(f"Failed to download: {response.status_code}")
