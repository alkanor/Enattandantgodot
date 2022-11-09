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


function Choice({ choices,
                  curChoice,
                  queryid }) {
  const associated = {
    YES: "success",
    NO: "secondary",
  };

  function setAnswer(event, answer) {
    console.log(answer);
    console.log(event);
  }

  function submit() {
    //http req
    console.log(queryid);
    console.log(curChoice);
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
        <Button variant="contained" onClick={submit}>Submit</Button>
      </div>
    </div>
  );
}

function QuestionChoice({ question,
                          choices,
                          curChoice,
                          queryid }) {

  return (
    <>
     <Grid container spacing={2} direction="row" justifyContent="center" alignItems="stretch">
      <Grid item xs={5}>
        <div style={{display: 'flex', justifyContent: 'center', alignItems: 'stretch'}}>
          {question}
        </div>
      </Grid>
      <Grid item xs={7}>
        <Choice choices={choices} queryid={queryid} curChoice={curChoice}/>
      </Grid>
     </Grid>
    </>
  );
}

function GraphDisplay({ graph }) {

  let myGraph = {nodes: graph.data.nodes.map( nodeobj => ({id: nodeobj.id, label: nodeobj.obj.toString()}) ),
                 edges: graph.data.edges.map( (edgeobj, index) => ({id: index, source: edgeobj.src, target: edgeobj.dst, label: edgeobj.obj.toString()}) )
                 };

  return (
      <>
        <Sigma graph={myGraph} settings={{drawEdges: true, clone: false}}>
          <RelativeSize initialSize={15}/>
          <RandomizeNodePositions/>
        </Sigma>
      </>
  );
}



export default function QuestionsForObject({objectId, queriesForObject, data}) {

    console.log("===========");
    console.log(objectId);
    console.log(queriesForObject);
    console.log(data);
    console.log("+++++++++++++");

    return (
    <>
      <Typography>
        {data && data.objects && JSON.stringify(data?.objects[objectId])}
      </Typography>

      {queriesForObject?.map(
        (queryid) => {
            let query = data.queries[queryid];
            console.log(query);
            console.log(queryid);
            console.log(data.questions[query.question]);

            return <QuestionChoice key={queryid} question={data.questions[query.question]} choices={data.choices} queryid={queryid} curChoice={data.existing_answers[queryid]}/>
        }
       )
      }
    </>);
}
