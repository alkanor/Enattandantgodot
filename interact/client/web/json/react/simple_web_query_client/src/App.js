import logo from './logo.svg';
import './App.css';
import { useState } from 'react';
import Pagination from '@mui/material/Pagination';

import BasicTabs from './MyComponents/MyTabs.js';


export default function App() {
  return <BasicTabs baseUrl="http://127.0.0.1:5000" />;
}
