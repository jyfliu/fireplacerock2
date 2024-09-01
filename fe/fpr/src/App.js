import React, { useState, useEffect } from 'react';
import { DndContext } from '@dnd-kit/core';
import Game from './Game';
import { Redirect, Switch, Route, Router } from 'react-router-dom'
import { ROUTES } from './RouterUtils';
import { history } from './pages/History.js'
import Home from './pages/Home';
import Collection from './pages/Collection';
import NotFound from './pages/NotFound';

function App() {
    return (
  <Router history={history}>
    <Switch>
      <Route exact={true} path={[ROUTES.ROOT, ROUTES.HOME]}>
        <Home />
      </Route>
      <Route path={ROUTES.GAME} >
        <Game />
      </Route>
      <Route path={ROUTES.COLLECTION}>
        <Collection />
      </Route>
      <Route path={'*'} >
        <NotFound />
      </Route>
    </Switch>
  </Router>
  );
};

export default App;
