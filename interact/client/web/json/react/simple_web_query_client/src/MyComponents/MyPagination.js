import { useState } from 'react';
import Pagination from '@mui/material/Pagination';


export default function BasicPagination({ Obj, data }) {
  const [currentPage, setCurrentPage] = useState(0);
  let ordered_queries = data ? Object.keys(data.ordered_queries) : [null];
  let item = data ? data.ordered_queries[ordered_queries[currentPage]] : null;
  let nrows = data ? Object.keys(data.ordered_queries).length : 0;

  function handleChange(event, value) {
    setCurrentPage(value-1);
    console.log(currentPage);
  }

  return (
    <>
      <Obj data={data} item={item}/>
      <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
        {data && (
            <Pagination count={nrows} shape="rounded" onChange={handleChange} style={{position:'absolute', bottom: 0}}/>
         )}
      </div>
    </>
  );
}
