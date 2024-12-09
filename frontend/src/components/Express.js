const Search = () => {
    const [exactSearch, setExactSearch] = useState('');
    const [results, setResult] = useState(null);
    const [userData, setUserData]=useState(null);
  
    const handleSearch = async () => {
      console.log('exact:', exactSearch);
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
          <div>
            <button onClick={handleSearch}>搜索</button>
          </div>
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
                  ? `C:/Code/ir/academic-garbage-final/snapshot/pdf/${item.title}.pdf`
                  : `C:/Code/ir/academic-garbage-final/snapshot/html/${item.title}.html`;
                  console.log(snapshotPath)
                  return(
                  <div key={index}>
                    <a href={item.url} target="_blank" rel="noopener noreferrer">
                      {item.title}
                    </a>
                    {}
                    <a herf={snapshotPath} target="_blank" rel="noopener noreferrer" style={{marginLeft:'10px'}}>快照</a>
                    <p>{item.content}</p>
                  </div>);
                })
              )}
              </div>
            </div>
          )}
        </div>
    );
  };