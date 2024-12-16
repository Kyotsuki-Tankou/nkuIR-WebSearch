## nkuIR-Websearch
Curriculum Project Assignment of Information Retrieve (IR)

2213919 Kyotsuki Tankou

College of Computer Science, Nankai University
### Brief
- Frontend: react
- Backend: python and elasticsearch
### Setup
For windows system, you can use `setup.bat` to setup automatically.

For other system or if you want to setup manually, you need to download and install proper [elasticsearch](https://www.elastic.co/cn/downloads/elasticsearch) and [ik-tokenizer](https://release.infinilabs.com/analysis-ik/), and use following command to setup the frontend and backend.

```bash
# Run your es with ik first
python ./backend/main.py #backend
cd ./frontend #frontend
npm start
```

### Usage
nkuIR-Websearch provides exact search, fuzzy search, regex search and domain-filtered search. Moreover, persionalized search sort and personalized recommendation(both offline and online) are integrated as well.

### Others
For the complete version, view on [OneDrive](https://5p6r2k-my.sharepoint.com/:f:/g/personal/kyotsuki_tankou_5p6r2k_onmicrosoft_com/EtM5csZMJlNNth_zdWH_hAQBUXy3d6O6aIFydfsx01_YQw?e=HB6j1w)