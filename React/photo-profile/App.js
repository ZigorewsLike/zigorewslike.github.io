import React, { Component } from 'react';
import './App.css';
import Content from './components/Content'
import { connect } from 'react-redux'
import Title from './components/Title'



class App extends Component {
  state = {
    name: this.props.user,
    link: 'https:' + this.props.link,
    icon: this.props.icon,
    photos: this.props.photos,
    year: this.props.year
  };
  render() {
    return (
        <div className="App">
          <header className="App-header">
          {//<img src={logo} className="App-logo" alt="logo" />
          }
            <Title 
              name={this.state.name} 
              link={this.state.link} 
              icon={this.state.icon}/>
          </header>
          <section className="App-body">
            <Content photos={this.state.photos} year={this.state.year}/>
          </section>
        </div>

    );
  }
}

function mapStateToProps(state){
  return {
    user: state.user,
    link: state.link,
    icon: state.icon,
    photos: state.photos,
    year: state.year
  }
}

export default connect(mapStateToProps)(App);