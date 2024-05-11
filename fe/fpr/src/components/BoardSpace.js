import React from 'react';
import { useDroppable } from '@dnd-kit/core';

import './BoardSpace.css';


export function BoardSpace(props) {
  const { isOver, setNodeRef } = useDroppable({
    id: props.id,
  });
  const { hiColor } = props;
  const style = {
    "background-color": isOver ? hiColor : undefined,
  };


  return (
    <div class="BoardSpace" ref={setNodeRef} style={style}>
      {props.children}
    </div>
  );
}
