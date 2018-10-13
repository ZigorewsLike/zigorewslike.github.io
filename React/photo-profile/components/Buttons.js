import React, { Component } from 'react';
import '../App.css';

class Buttons extends Component{
  constructor(props) {
    super(props);
    this.state = {
      value: 0,
    };
  };
  handleCheckPlus = () => {
    this.setState({value: this.state.value + 1});
  };
  handleCheckMinus = () => {
    this.setState({value: this.state.value - 1});
  };
  render(){
    return(
      <div>
        <div className='butt'><button onClick = {this.handleCheckPlus}>+</button>
        <section className = 'elem'>ЗНАЧЕНИЕ : {this.state.value}</section>
        <button onClick = {this.handleCheckMinus}>-</button></div>
      </div>
    );
  }
  
}

export default Buttons;
  