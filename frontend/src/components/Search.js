// src/components/Search.js
import React, { useEffect,useState } from 'react';

const Search = () => {
  const [exactSearch, setExactSearch] = useState('');
  const [fuzzySearch, setFuzzySearch] = useState('');
  const [regexSearch, setRegexSearch] = useState('');
  const [domainSearch, setdomainSearch] = useState('');
  const [querySize, setQuerySize] = useState('');
  const [results, setResult] = useState(null);
  const [userData, setUserData]=useState(null);

  const handleSearch = async () => {
    console.log('exact:', exactSearch);
    console.log('fuzze:', fuzzySearch);
    console.log('regex:', regexSearch);
    console.log('domain:', domainSearch);
    console.log('querysize:',querySize);
    fetchUserData();
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
           setResult(data);
           console.log(data)
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
  const fetchUserData = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/get_user_info', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      console.log(data.success,data.message)
      console.log(data)
      if (data.success) {
        setUserData(data.userdata);
      } else {
        alert(data.message);
      }
    } catch (error) {
      console.error('获取用户信息失败:', error);
    }
  };

  useEffect(() => {
    fetchUserData();
  }, []);

  return (
    <div>
    <div style={styles.container}>
      <div style={styles.searchBox}>
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
          <div>返回条目数量（部分搜索例如正则搜索消耗资源较大，请合理设置）</div>
          <input
          type="text"
          placeholder="默认为20"
          value={querySize}
          onChange={(e) => setQuerySize(e.target.value)}
        />
        </div>
        <div>
          <button onClick={handleSearch}>搜索</button>
        </div>
      </div>
        <div style={styles.historyBox}>
          <h2>搜索历史</h2>
          {userData && userData.history && userData.history.length > 0 ? (
            <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.tableHeader}>精确搜索</th>
                <th style={styles.tableHeader}>模糊搜索</th>
                <th style={styles.tableHeader}>正则搜索</th>
                <th style={styles.tableHeader}>域名</th>
                <th style={styles.tableHeader}>大小</th>
              </tr>
            </thead>
            <tbody>
              {userData.history.slice(-5).map((item, index) => (
                <tr key={index}>
                  <td style={styles.tableCell}>{item.exact}</td>
                  <td style={styles.tableCell}>{item.fuzzy}</td>
                  <td style={styles.tableCell}>{item.regex}</td>
                  <td style={styles.tableCell}>{item.domain}</td>
                  <td style={styles.tableCell}>{item.size}</td>
                </tr>
              ))}
            </tbody>
          </table>
          ) : (
            <p>没有搜索历史</p>
          )}
        </div>
      </div>
        {results && (
          <div>
            <h3>搜索结果：</h3>
            {results.res_list.length === 0 ? (
              <p>未检索出对应内容</p>
            ) : (
              results.res_list.map((item, index) => {
                const snapshotPath = item.content.endsWith('.pdf')
                ? `http://127.0.0.1:5000/static/snapshot/pdfs/${item.title}.pdf`
                : `http://127.0.0.1:5000/static/snapshot/html/${item.title}.html`;
                console.log(snapshotPath)
                return(
                <div key={index}>
                  <a href={item.url} target="_blank" rel="noopener noreferrer">
                    {item.title}
                  </a>
                  {}
                  <a href={snapshotPath} target="_blank" rel="noopener noreferrer" style={{marginLeft:'10px'}}>快照</a>
                  <p>{item.content}</p>
                </div>);
              })
            )}
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <div>
                <h3>站内推荐：</h3>
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
                <h3>联网推荐</h3>
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

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'flex-start',
    padding: '20px',
  },
  searchBox: {
    flex: 1,
    marginRight: '20px',
    width: '80%'
  },
  historyBox: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  historyTitle: {
    textAlign: 'center',
  },
  table: {
    width: '80%',
    borderCollapse: 'collapse',
    marginTop: '20px',
  },
  tableHeader: {
    border: '1px solid #ddd',
    padding: '8px',
    textAlign: 'center',
  },
  tableCell: {
    border: '1px solid #ddd',
    padding: '8px',
    textAlign: 'center',
  },
};

export default Search;

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