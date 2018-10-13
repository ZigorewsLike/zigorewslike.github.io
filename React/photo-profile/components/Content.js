import React, { Component } from 'react';
import '../App.css';
import Photo from './Photo'
import { connect } from 'react-redux'

class Content extends Component{
    
  constructor(props) {
    super(props);
    this.state = {
      value: 2018,
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
        <div className="DataText">
            <h3>Фотографии за {this.state.value} год</h3>
            <hr className="hr"/>
            <Photo year={this.state.value}/>
            <h3>Фотографии за {this.state.value-2} год</h3>
            <hr className="hr"/>
            <Photo year={this.state.value-2}/>
           
        </div>
      </div>
    );
  }
  
}

function mapStateToProps (state) {
    return {
    page: state.page
    }
    }
export default connect(mapStateToProps)(Content)