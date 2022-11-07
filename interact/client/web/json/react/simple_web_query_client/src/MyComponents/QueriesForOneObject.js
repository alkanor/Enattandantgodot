import * as React from 'react';
import Typography from '@mui/material/Typography';


const ONEOBJET_DATA = [{'objs': [{'id': 3, 'graphid': 100, 'tablename': 'basicG', 'type': 'persistent.base_type.base_entity::_BasicEntity'}], 'questions': [{'id': 3, 'question': 'Is directed?', 'tablename': 'basicQ', 'type': 'persistent.base_type.base_entity::_BasicEntity'}, {'id': 4, 'question': 'Has root?', 'tablename': 'basicQ', 'type': 'persistent.base_type.base_entity::_BasicEntity'}], 'queries': [[11, 3, 3], [12, 3, 4]], 'ordered_queries': {3: [11, 12]}}]


export default function QueriesForOneObject({data}) {
    const [baseList, setBaseList] = React.useState(
        ONEOBJET_DATA
     );
    return (
    <>
      <Typography>
        {JSON.stringify(data)}
      </Typography>
    </>);
}
