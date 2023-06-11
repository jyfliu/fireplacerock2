import React from 'react';
import { useDroppable } from '@dnd-kit/core';

import './BoardSpace.css';


export function BoardSpace(props) {
  const { isOver, setNodeRef } = useDroppable({
    id: props.id,
  });
  const style = {
    "background-color": isOver ? '#449944' : undefined,
  };
  
  
  return (
    <div class="BoardSpace" ref={setNodeRef} style={style}>
      {props.children}
    </div>
  );
}
