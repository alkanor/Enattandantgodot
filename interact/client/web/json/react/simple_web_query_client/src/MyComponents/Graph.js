import { useEffect, useRef, useState } from "react";
import G6 from "@antv/g6";

let graph = null;

const Graph = ({inputData}) => {
  const [data, setData] = useState(inputData);

  const ref = useRef(null);

  useEffect(() => {
    if (!graph) {
      graph = new G6.Graph({
        container: ref.current,
        width: 600,
        height: 600,
        modes: {
          default: ["drag-canvas", "zoom-canvas", "drag-node"],
        },
        layout: {
            type: 'force',
            preventOverlap: true,
            linkDistance: 200,
        }
      });
    }

    graph.data(data);
    graph.render();

    return () => {
      graph.changeData(data);
    };
  }, [data]);

  const handleClick = () => {
    setData(inputData);
  };
  return (
    <>
      <button onClick={handleClick}>Reload data</button>
      <div ref={ref}></div>
    </>
  );
};

export default Graph;