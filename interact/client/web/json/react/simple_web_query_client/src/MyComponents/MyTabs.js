import * as React from 'react';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

import BasicPagination from './MyPagination.js';
import QueriesForOneObject from './QueriesForOneObject.js';
import StackedObjectsQueries from './StackedObjectsQueries.js';

import RefreshIcon from '@mui/icons-material/Refresh';



interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  };
}

export default function BasicTabs({baseUrl, maxSimultaneousQuestions = 200}) {
  const [value, setValue] = React.useState(0);
  const [error, setError] = React.useState('');
  const [mainData, setMainData] = React.useState([null, null, null]);

  const urls = ["/next", "/next_grouped", "/next_forobjectgroup"];

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
    mainData[newValue] || query(newValue);
  };

  const forceChange = (value: number) => {
    query(value);
  };

  function query(index_query) {
    fetch(baseUrl+urls[index_query]+"/"+maxSimultaneousQuestions.toString())
      .then((response) => response.json())
      .then((data) => {
          setMainData( mainData.map( (bdata, index) => index_query == index ?
                {
                    choices: data.answer.choices,
                    /*objs: data.objs,
                    queries: data.queries.map( (query) => {return {id: query[0], obj: query[1], question: query[2]}} ),
                    questions: data.questions.map( (question) => {return {id: question.id, question: question.question}} ),
                    */
                    objs: data.objs.reduce(
                        function (dict, acc) {
                            return {...dict, ...{[acc.id]: acc}};
                        }, {}),
                    queries: data.queries.reduce(
                        function (dict, query) {
                            return {...dict, ...{[query[0]]: {obj: query[1], question: query[2]}}};
                        }, {}),
                    ordered_queries: data.ordered_queries,
                    questions: data.questions.reduce(
                        function (dict, acc) {
                            return {...dict, ...{[acc.id]: acc.question}};
                        }, {}),
                    existing_answers: data.existing_answers,  /*&& Object.keys(data.existing_answers).reduce(
                        function (dict, acc) {
                            return {...dict, ...{queryid: acc, ans: data.existing_answers[acc].ans}};
                        }, {}),*/
                } : bdata ));
          setError('');
        },
        (error) => {
          setError(error.message);
        }
      );
  }

  React.useEffect( () => query(0), [] );

  return (
    <>
     <Box sx={{ width: '100%' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={value} onChange={handleChange} aria-label="basic tabs example">
          <Tab label="Multiple queries for one object" {...a11yProps(0)} />
          <Tab label="Multiple queries per multiple objects" {...a11yProps(1)} />
          <Tab label="Multiple stacked queries" {...a11yProps(2)} />
        </Tabs>
      </Box>

      {[QueriesForOneObject, StackedObjectsQueries, StackedObjectsQueries].map(
        (Obj, i) => {
          return (
            <TabPanel value={value} index={i} key={i}>
              <RefreshIcon onClick={ () => forceChange(i) }/>
              <BasicPagination Obj={Obj} data={mainData[i]} baseUrl={baseUrl}/>
            </TabPanel>
        );
       })
      }
     </Box>

     {error && (
        <p className="error"> {error} </p>
     )}
    </>
  );
}