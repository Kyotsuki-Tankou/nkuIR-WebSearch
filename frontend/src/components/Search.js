// src/components/Search.js
import React, { useState } from 'react';

const Search = () => {
  const [exactSearch, setExactSearch] = useState('');
  const [fuzzySearch, setFuzzySearch] = useState('');
  const [regexSearch, setRegexSearch] = useState('');
  const [domainSearch, setdomainSearch] = useState('');
  const [querySize, setQuerySize] = useState('');
  const [results, setResult] = useState(null);

  const handleSearch = async () => {
    console.log('exact:', exactSearch);
    console.log('fuzze:', fuzzySearch);
    console.log('regex:', regexSearch);
    console.log('domain:', domainSearch);
    console.log('querysize:',querySize);
    try{
        const response=await fetch('http://127.0.0.1:5000/search',{
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            },
            body: JSON.stringify({exactSearch,fuzzySearch,regexSearch,domainSearch,querySize}),
        });
        const data=await response.json();
        if(data.success)
        {
            /*显示搜索结果，结果包括：
            搜索主体：
            每个搜索的主体结果包括
                标题（带超链接）->res_list[i].title, res_list[i].url
                正文（res_list[i].content）

            右上推荐栏（每行一个）：
                标题（带超链接）->rec1_list[i].title, rec1_list[i].url
            右下推荐栏（每行一个）：
                标题（带超链接）->rec2_list[i].title, rec2_list[i].url
            */
           setResult(data);
        }
        else
        {
            alert('出现错误：'+data.message);
        }
    }
    catch(error){
        console.log('Error:',error)
    }
  };

  return (
    <div>
      <h2>搜索</h2>
      <div>
        <div>精确搜索</div>
        <input
        type="text"
        placeholder="请使用^隔开不同的搜索项"
        value={exactSearch}
        onChange={(e) => setExactSearch(e.target.value)}
      />
      </div>
      <div>
        <div>模糊搜索</div>
        <input
        type="text"
        placeholder="请使用^隔开不同的搜索项"
        value={fuzzySearch}
        onChange={(e) => setFuzzySearch(e.target.value)}
      />
      </div>
      <div>
        <div>正则表达式搜索</div>
        <input
        type="text"
        placeholder="请使用^隔开不同的搜索项"
        value={regexSearch}
        onChange={(e) => setRegexSearch(e.target.value)}
      />
      </div>
      <div>
        <div>指定域名</div>
        <input
        type="text"
        placeholder="指定域名"
        value={domainSearch}
        onChange={(e) => setdomainSearch(e.target.value)}
      />
      </div>
      <div>
        <div>返回条目数量</div>
        <input
        type="text"
        placeholder="默认为20，部分搜索例如正则搜索消耗资源较大，请合理设置"
        value={querySize}
        onChange={(e) => setQuerySize(e.target.value)}
      />
      </div>
      <div>
        <button onClick={handleSearch}>搜索</button>
      </div>
      {results && (
        <div>
          <h3>搜索主体：</h3>
          {results.res_list.length === 0 ? (
            <p>未检索出对应内容</p>
          ) : (
            results.res_list.map((item, index) => (
              <div key={index}>
                <a href={item.url} target="_blank" rel="noopener noreferrer">
                  {item.title}
                </a>
                <p>{item.content}</p>
              </div>
            ))
          )}
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <div>
              <h3>右上推荐栏：</h3>
              {results.rec1_list.length === 0 ? (
                <p>未检索出对应内容</p>
              ) : (
                results.rec1_list.map((item, index) => (
                  <div key={index}>
                    <a href={item.url} target="_blank" rel="noopener noreferrer">
                      {item.title}
                    </a>
                  </div>
                ))
              )}
            </div>
            <div>
              <h3>右下推荐栏：</h3>
              {results.rec2_list.length === 0 ? (
                <p>未检索出对应内容</p>
              ) : (
                results.rec2_list.map((item, index) => (
                  <div key={index}>
                    <a href={item.url} target="_blank" rel="noopener noreferrer">
                      {item.title}
                    </a>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Search;
