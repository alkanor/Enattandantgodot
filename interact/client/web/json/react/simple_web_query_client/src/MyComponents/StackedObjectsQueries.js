import * as React from 'react';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';

import QuestionsForObject from './ObjectAndQuestions.js';


export default function StackedObjectsQueries({data, item, submit}) {
    let objectKeys = item && Object.keys(item);

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
     {item && objectKeys.map(
        (objid) => {
          return (
            <Paper elevation={3} key={objid}>
                <QuestionsForObject objectId={objid} queriesForObject={item[objid]} data={data} submit={submit}/>
            </Paper>
        );
       })
      }
    </Box>
    );
}
