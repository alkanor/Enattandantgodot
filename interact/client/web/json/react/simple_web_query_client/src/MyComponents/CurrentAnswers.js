import * as React from 'react';
import Button from '@mui/material/Button';
import SendIcon from '@mui/icons-material/Send';


export default function CurrentAnswers({Obj, data, item, resetAnswers, baseUrl}) {
    const [answerPerQuery, setanswerPerQuery] = React.useState({});
    const [error, setError] = React.useState('');

    const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    };

    function resetAnswers() {
        setanswerPerQuery({});
    }

    function submitAnswers() {
        fetch(baseUrl+"/processed", {...requestOptions, body: JSON.stringify(
            Object.keys(answerPerQuery).map ( (queryid) => {return {query: {id: queryid}, answer: answerPerQuery[queryid]}}))
           }
         )
         .then((response) => response.json())
         .then( (ok) => {resetAnswers();}, (error) => {setError(error.message);} )
    }

    function submitAnswer(queryid, answer, saveOnly=false) {
        setanswerPerQuery({...answerPerQuery, ...{[queryid]: answer}});
        if(!saveOnly) {
            fetch(baseUrl+"/processed", {...requestOptions, body: JSON.stringify( {query: {id: queryid}, answer: answer} )
                }
             )
             .then((response) => response.json())
             .then( (ok) => {
                let keys = Object.keys(answerPerQuery);
                console.log(keys);
                setanswerPerQuery(keys.filter( (qid) => qid != queryid )
                                        .reduce( (dict, qid) => {return {...dict, ...{[qid]: answerPerQuery[qid]}}}, {})
                                  );
             }, (error) => {setError(error.message);} )
        }
    }

    if (resetAnswers.mustBeResetted) {
        resetAnswers();
        resetAnswers.resetReset(false);
    }

    return (
    <>
      <Obj data={data} item={item} submit={submitAnswer}/>
      <Button variant="contained" endIcon={<SendIcon />} onClick={submitAnswers}>
        Send All
      </Button>

      {error && (
        <p className="error"> {error} </p>
      )}
    </>);
}
