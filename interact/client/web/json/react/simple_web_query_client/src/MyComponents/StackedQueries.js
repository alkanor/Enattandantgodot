import * as React from 'react';
import StackedObjectsQueries from './StackedObjectsQueries';


export default function StackedQueries({ data, item }) {
    return (
      <StackedObjectsQueries data={data} item={item} checkStackedPerObject={false}/>
    );
}

