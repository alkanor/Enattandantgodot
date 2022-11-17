import * as React from 'react';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';

import QuestionsForObject from './ObjectAndQuestions.js';


export default function QueriesForOneObject({data, item, submit}) {
    return (
     <Box
        sx={{
        display: 'flex',
        flexWrap: 'wrap',
        '& > :not(style)': {
          m: 1,
        },
        minHeight: 500,
      }}
     >
     {item &&
         <Paper elevation={3}>
             <QuestionsForObject objectId = {data.queries[item[0]].obj}
                                queriesForObject = {item}
                                data = {data}
                                submit = {submit}/>
         </Paper>
      }
    </Box>
    );
}
