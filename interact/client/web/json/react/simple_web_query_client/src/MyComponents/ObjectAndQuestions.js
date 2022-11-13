import { useState } from 'react';
import { success, secondary } from '@mui/material/colors';
import Pagination from '@mui/material/Pagination';
import Grid from '@mui/material/Grid';
import Button from '@mui/material/Button';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';
import {Sigma, RandomizeNodePositions, RelativeSize} from 'react-sigma';
import Typography from '@mui/material/Typography';
import G6 from "@antv/g6";

import Graph from './Graph.js';


function Choice({ choices,
                  curChoice,
                  queryid,
                  submit}) {
  const [curAnswer, setCurAnswer] = useState(null);

  const associated = {
    YES: "success",
    NO: "secondary",
  };

  function setAnswer(event, answer) {
    setCurAnswer(answer);
    submit(queryid, answer, true);
  }

  function submitForm() {
    //http req
    submit(queryid, curAnswer);
  }

  return (
    <div style={{display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'left'}}>
      <FormControl>
        <FormLabel>Answer</FormLabel>
        <RadioGroup
          row
          name="row-radio-buttons-answer"
          onChange={setAnswer}
          defaultValue={curChoice?.ans}
        >
          {choices.map(choice =>
               <FormControlLabel key={choice} value={choice} control={<Radio />} label={choice} color={associated[choice] || "default"}/>
           )}
        </RadioGroup>
      </FormControl>
      <div>
        <Button variant="contained" onClick={submitForm}>Submit</Button>
      </div>
    </div>
  );
}

function QuestionChoice({ question,
                          choices,
                          curChoice,
                          queryid,
                          submit}) {

  return (
    <>
     <Grid container spacing={2} direction="row" justifyContent="center" alignItems="stretch">
      <Grid item xs={5}>
        <div style={{display: 'flex', justifyContent: 'center', alignItems: 'stretch'}}>
          {question}
        </div>
      </Grid>
      <Grid item xs={7}>
        <Choice choices={choices} queryid={queryid} curChoice={curChoice} submit={submit}/>
      </Grid>
     </Grid>
    </>
  );
}

function GraphDisplay({ graph }) {

  console.log(graph);
  let myGraph = {nodes: graph.data.nodes.map( nodeobj => ({id: nodeobj.id.toString(), label: nodeobj.obj.toString()}) ),
                 edges: graph.data.edges.map(
                    (edgeobj, index) => ({
                        source: edgeobj.src.toString(),
                        target: edgeobj.dst.toString(),
                        label: edgeobj.obj.toString(),
                        type:  edgeobj.src ==  edgeobj.dst ? 'loop' : 'line',
                        style: graph?.metadata?.properties.includes('Directed') && {
                              endArrow: {
                              path: G6.Arrow.triangle(10, 20, 1),
                              fill: '#f00',
                            }
                        }
                    }) )
                 };

  return (
      <>
        <Graph inputData={myGraph} />
      </>
  );
}



export default function QuestionsForObject({objectId, queriesForObject, data, submit}) {
    return (
     <>
      <Typography>
        {data && data.objs && data?.objs[objectId].tablename != "GraphJson" && JSON.stringify(data?.objs[objectId])}
      </Typography>

      {data && data.objs && data.objs[objectId].tablename == "GraphJson" && <GraphDisplay graph={JSON.parse(data.objs[objectId].graph_json_as_string)} />}

      {queriesForObject?.map(
        (queryid) => {
            let query = data.queries[queryid];
            return <QuestionChoice key={queryid}
                            question={data.questions[query.question]}
                            choices={data.choices}
                            queryid={queryid}
                            curChoice={data.existing_answers && data.existing_answers[queryid]}
                            submit={submit}/>
        }
       )
      }
     </>);
}
