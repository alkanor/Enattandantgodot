import logo from './logo.svg';
import './App.css';
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


function Choice({ choices,
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
  }

  return (
    <div style={{display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'left'}}>
      <FormControl>
        <FormLabel>Answer</FormLabel>
        <RadioGroup
          row
          name="row-radio-buttons-answer"
          onChange={setAnswer}
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
        <Choice choices={choices} queryid={queryid}/>
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

function GraphQuestionChoice({ graphQuestionChoiceItem }) {
  return (
    <>
      <GraphDisplay graph={ JSON.parse(graphQuestionChoiceItem.object.graph_json_as_string) }/>
      <QuestionChoice question={graphQuestionChoiceItem.question.question} choices={graphQuestionChoiceItem.answer.choices} queryid={graphQuestionChoiceItem.query}/>
    </>
  );
}


function FullViewWithControls({ data }) {
  const [currentGraph, setCurrentGraph] = useState(0);
  let nrows = data.length;
  let item = data[currentGraph];

  function handleChange(event, value) {
    setCurrentGraph(value-1);
  }

  return (
    <>
      <GraphQuestionChoice graphQuestionChoiceItem={item}/>
      <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
        <Pagination count={nrows} shape="rounded" onChange={handleChange} style={{position:'absolute', bottom: 0}}/>
      </div>
    </>
  );
}


const GRAPHQUESTION = [{"answer":{"choices":["YES","NO","UNKNOWN"],"type":"persistent.model.interact.answers.yes_no_unknown::YesNoUnknown"},"object":{"graph_json_as_string":"{\"metadata\": {\"properties\": [\"Directed\"], \"nodetype\": \"builtins::int\", \"edgetype\": \"builtins::str\"}, \"data\": {\"nodes\": [{\"id\": 0, \"obj\": 0}, {\"id\": 1, \"obj\": 3}, {\"id\": 2, \"obj\": 4}, {\"id\": 3, \"obj\": 5}, {\"id\": 4, \"obj\": 1}, {\"id\": 5, \"obj\": 9}, {\"id\": 6, \"obj\": 2}, {\"id\": 7, \"obj\": 7}, {\"id\": 8, \"obj\": 8}, {\"id\": 9, \"obj\": 6}, {\"id\": 10, \"obj\": 10}], \"edges\": [{\"src\": 0, \"dst\": 10, \"obj\": \"link[0-0]\"}, {\"src\": 0, \"dst\": 9, \"obj\": \"link[0-1]\"}, {\"src\": 4, \"dst\": 1, \"obj\": \"link[1-0]\"}, {\"src\": 4, \"dst\": 4, \"obj\": \"link[1-1]\"}, {\"src\": 6, \"dst\": 4, \"obj\": \"link[2-0]\"}, {\"src\": 6, \"dst\": 2, \"obj\": \"link[2-1]\"}, {\"src\": 1, \"dst\": 3, \"obj\": \"link[3-0]\"}, {\"src\": 1, \"dst\": 5, \"obj\": \"link[3-1]\"}, {\"src\": 1, \"dst\": 4, \"obj\": \"link[3-2]\"}, {\"src\": 2, \"dst\": 4, \"obj\": \"link[4-0]\"}, {\"src\": 3, \"dst\": 6, \"obj\": \"link[5-0]\"}, {\"src\": 9, \"dst\": 5, \"obj\": \"link[6-0]\"}, {\"src\": 9, \"dst\": 7, \"obj\": \"link[6-1]\"}, {\"src\": 7, \"dst\": 3, \"obj\": \"link[7-0]\"}, {\"src\": 7, \"dst\": 0, \"obj\": \"link[7-1]\"}, {\"src\": 8, \"dst\": 10, \"obj\": \"link[8-0]\"}, {\"src\": 8, \"dst\": 0, \"obj\": \"link[8-1]\"}, {\"src\": 5, \"dst\": 5, \"obj\": \"link[9-0]\"}, {\"src\": 10, \"dst\": 3, \"obj\": \"link[10-0]\"}]}}","id":1,"tablename":"GraphJson","type":"persistent.base_type.base_entity::_BasicEntity"},"query":2,"question":{"id":2,"question":"Is constraint weakly_connected_constraint verified? (evaluated to True)","tablename":"GraphPropertyQuestion","type":"persistent.base_type.base_entity::_BasicEntity"}},
    {"answer":{"choices":["YES","NO","UNKNOWN"],"type":"persistent.model.interact.answers.yes_no_unknown::YesNoUnknown"},"object":{"graph_json_as_string":"{\"metadata\": {\"properties\": [\"Directed\"], \"nodetype\": \"builtins::int\", \"edgetype\": \"builtins::str\"}, \"data\": {\"nodes\": [{\"id\": 0, \"obj\": 0}, {\"id\": 1, \"obj\": 3}, {\"id\": 2, \"obj\": 4}, {\"id\": 3, \"obj\": 5}, {\"id\": 4, \"obj\": 1}, {\"id\": 5, \"obj\": 9}, {\"id\": 6, \"obj\": 2}, {\"id\": 7, \"obj\": 7}, {\"id\": 8, \"obj\": 8}, {\"id\": 9, \"obj\": 6}, {\"id\": 10, \"obj\": 10}], \"edges\": [{\"src\": 0, \"dst\": 10, \"obj\": \"link[0-0]\"}, {\"src\": 0, \"dst\": 9, \"obj\": \"link[0-1]\"}, {\"src\": 4, \"dst\": 1, \"obj\": \"link[1-0]\"}, {\"src\": 4, \"dst\": 4, \"obj\": \"link[1-1]\"}, {\"src\": 6, \"dst\": 4, \"obj\": \"link[2-0]\"}, {\"src\": 6, \"dst\": 2, \"obj\": \"link[2-1]\"}, {\"src\": 1, \"dst\": 3, \"obj\": \"link[3-0]\"}, {\"src\": 1, \"dst\": 5, \"obj\": \"link[3-1]\"}, {\"src\": 1, \"dst\": 4, \"obj\": \"link[3-2]\"}, {\"src\": 2, \"dst\": 4, \"obj\": \"link[4-0]\"}, {\"src\": 3, \"dst\": 6, \"obj\": \"link[5-0]\"}, {\"src\": 9, \"dst\": 5, \"obj\": \"link[6-0]\"}, {\"src\": 9, \"dst\": 7, \"obj\": \"link[6-1]\"}, {\"src\": 7, \"dst\": 3, \"obj\": \"link[7-0]\"}, {\"src\": 7, \"dst\": 0, \"obj\": \"link[7-1]\"}, {\"src\": 8, \"dst\": 10, \"obj\": \"link[8-0]\"}, {\"src\": 8, \"dst\": 0, \"obj\": \"link[8-1]\"}, {\"src\": 5, \"dst\": 5, \"obj\": \"link[9-0]\"}, {\"src\": 10, \"dst\": 3, \"obj\": \"link[10-0]\"}]}}","id":1,"tablename":"GraphJson","type":"persistent.base_type.base_entity::_BasicEntity"},"query":2,"question":{"id":2,"question":"Is constraint weakly_connected_constraint verified? (evaluated to True)","tablename":"GraphPropertyQuestion","type":"persistent.base_type.base_entity::_BasicEntity"}},
    {"answer":{"choices":["YES","NO","UNKNOWN"],"type":"persistent.model.interact.answers.yes_no_unknown::YesNoUnknown"},"object":{"graph_json_as_string":"{\"metadata\": {\"properties\": [\"Directed\"], \"nodetype\": \"builtins::int\", \"edgetype\": \"builtins::str\"}, \"data\": {\"nodes\": [{\"id\": 0, \"obj\": 0}, {\"id\": 1, \"obj\": 3}, {\"id\": 2, \"obj\": 4}, {\"id\": 3, \"obj\": 5}, {\"id\": 4, \"obj\": 1}, {\"id\": 5, \"obj\": 9}, {\"id\": 6, \"obj\": 2}, {\"id\": 7, \"obj\": 7}, {\"id\": 8, \"obj\": 8}, {\"id\": 9, \"obj\": 6}, {\"id\": 10, \"obj\": 10}], \"edges\": [{\"src\": 0, \"dst\": 10, \"obj\": \"link[0-0]\"}, {\"src\": 0, \"dst\": 9, \"obj\": \"link[0-1]\"}, {\"src\": 4, \"dst\": 1, \"obj\": \"link[1-0]\"}, {\"src\": 4, \"dst\": 4, \"obj\": \"link[1-1]\"}, {\"src\": 6, \"dst\": 4, \"obj\": \"link[2-0]\"}, {\"src\": 6, \"dst\": 2, \"obj\": \"link[2-1]\"}, {\"src\": 1, \"dst\": 3, \"obj\": \"link[3-0]\"}, {\"src\": 1, \"dst\": 5, \"obj\": \"link[3-1]\"}, {\"src\": 1, \"dst\": 4, \"obj\": \"link[3-2]\"}, {\"src\": 2, \"dst\": 4, \"obj\": \"link[4-0]\"}, {\"src\": 3, \"dst\": 6, \"obj\": \"link[5-0]\"}, {\"src\": 9, \"dst\": 5, \"obj\": \"link[6-0]\"}, {\"src\": 9, \"dst\": 7, \"obj\": \"link[6-1]\"}, {\"src\": 7, \"dst\": 3, \"obj\": \"link[7-0]\"}, {\"src\": 7, \"dst\": 0, \"obj\": \"link[7-1]\"}, {\"src\": 8, \"dst\": 10, \"obj\": \"link[8-0]\"}, {\"src\": 8, \"dst\": 0, \"obj\": \"link[8-1]\"}, {\"src\": 5, \"dst\": 5, \"obj\": \"link[9-0]\"}, {\"src\": 10, \"dst\": 3, \"obj\": \"link[10-0]\"}]}}","id":1,"tablename":"GraphJson","type":"persistent.base_type.base_entity::_BasicEntity"},"query":2,"question":{"id":2,"question":"Is constraint weakly_connected_constraint verified? (evaluated to True)","tablename":"GraphPropertyQuestion","type":"persistent.base_type.base_entity::_BasicEntity"}}];

export default function App() {
  const [baseList, setBaseList] = useState(
    GRAPHQUESTION
  );
  return <FullViewWithControls data={baseList} />;
}
