import * as React from 'react';
import Typography from '@mui/material/Typography';

// uses QueriesForOneObject


export default function StackedObjectsQueries({data, item, checkStackedPerObject = true}) {
    const [baseList, setBaseList] = React.useState(data);

    return (
     <>
      <Typography>
        {JSON.stringify(item)}
      </Typography>
     </>
    );
}

/*
{"choices":["YES","NO","UNKNOWN"],
"objs":[{"graphid":1,"id":1,"tablename":"basicG","type":"persistent.base_type.base_entity::_BasicEntity"},
{"graphid":10,"id":2,"tablename":"basicG","type":"persistent.base_type.base_entity::_BasicEntity"},
{"graphid":100,"id":3,"tablename":"basicG","type":"persistent.base_type.base_entity::_BasicEntity"}],

"queries":[{"id":1,"obj":1,"question":1},{"id":2,"obj":1,"question":2},{"id":3,"obj":1,"question":3},{"id":4,"obj":1,"question":4},{"id":7,"obj":2,"question":3},{"id":8,"obj":2,"question":4},{"id":5,"obj":2,"question":1},{"id":10,"obj":3,"question":2},{"id":11,"obj":3,"question":3},{"id":12,"obj":3,"question":4}],

"ordered_queries":{"5":{"1":[1,2,3,4]},"6":{"1":[2],"2":[7,8]},"7":{"1":[3],"3":[11,12]},"8":{"2":[5],"3":[10]}},

"questions":[{"id":1,"question":"Is acyclic?"},{"id":2,"question":"Is tree?"},{"id":3,"question":"Is directed?"},{"id":4,"question":"Has root?"}],

"existing_answers":{"queryid":"12","ans":"NO"}}
*/