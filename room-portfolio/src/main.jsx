/* eslint-disable react-refresh/only-export-components */
import './style.css';

import { lazy, Suspense } from 'react';
import ReactDOM from 'react-dom/client';

import RoomBoot from './RoomBoot.jsx';

const Experience = lazy(() => import('./Experience.jsx'));

const root = ReactDOM.createRoot(document.querySelector('#root'));

root.render(
    <Suspense fallback={<RoomBoot />}>
        <Experience />
    </Suspense>
);
