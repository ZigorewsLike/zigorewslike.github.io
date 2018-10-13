import React, { Component } from 'react';
import '../App.css';
import Menu from '../Menu.png';


class Title extends Component {
    render() {
      return (
        <div className="row">
            <div className="Title">
              <div className="ElementTitle1">
                <button className="Button_UnVis">
                  <img src={Menu} className="App-logo" alt="IMG"/>
                </button>
              </div>
              <div className="ElementTitle2">
                <h1>ФОТОКАРТОЧКИ</h1>
              </div>

              <div className="ElementTitle3">
                <a href={this.props.link}>{ this.props.name }</a>
                <img className="iconProf" src={this.props.icon} key={1} alt="Img"/>
              </div>
            </div>
        </div>
      );
    }
}

  export default (Title);