import { useState } from 'react';
import Pagination from '@mui/material/Pagination';

import CurrentAnswers from './CurrentAnswers.js';


export default function BasicPagination({ Obj, data, baseUrl }) {
  const [currentPage, setCurrentPage] = useState(0);
  const [mustBeResetted, resetAnswers] = useState(false);
  let ordered_queries = data ? Object.keys(data.ordered_queries) : [null];
  let item = data ? data.ordered_queries[ordered_queries[currentPage]] : null;
  let nrows = data ? Object.keys(data.ordered_queries).length : 0;

  function handleChange(event, value) {
    setCurrentPage(value-1);
    resetAnswers(true);
    console.log(currentPage);
  }

  return (
    <>
      <CurrentAnswers Obj={Obj} data={data} item={item} resetAnswers={{mustBeResetted: mustBeResetted, resetReset: resetAnswers}} baseUrl={baseUrl} />
      <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
        {data && (
            <Pagination count={nrows} shape="rounded" onChange={handleChange} style={{position:'absolute', bottom: 0}}/>
         )}
      </div>
    </>
  );
}
