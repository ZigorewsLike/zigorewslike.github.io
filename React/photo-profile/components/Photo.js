import React, { Component } from 'react';
import '../App.css';
import Img1 from '../1.jpg';
import Img2 from '../2.jpg';
import Img3 from '../3.jpg';
import Img4 from '../4.jpg';
import Img5 from '../5.jpg';
import Img6 from '../6.jpg';
import Img7 from '../7.jpg';
import Img8 from '../8.jpg';
import Img9 from '../9.jpg';
import Img10 from '../10.jpg';
import Img11 from '../11.jpg';

const images = [
  { url: Img1, id: '1', year: '2018'},
  { url: Img2, id: '2', year: '2018'},
  { url: Img3, id: '3', year: '2018'},
  { url: Img4, id: '4', year: '2018'},
  { url: Img5, id: '5', year: '2018'},
  { url: Img6, id: '6', year: '2018'},
  { url: Img7, id: '7', year: '2017'},
  { url: Img8, id: '8', year: '2017'},
  { url: Img9, id: '9', year: '2017'},
  { url: Img10, id: '10', year: '2017'},
  { url: Img11, id: '11', year: '2017'},
]

class Photo extends Component{
  
  render(){
    
      const imgs = images.map((el) => {
        if (el.year == '2018') {
          return (
            <img src={el.url} key={el.url} className="Pict" alt="img"/>
          )} 
        else if(el = images == '2016') {
            return (
                <img src={el.url} key={el.url} className="Pict" alt="img"/>
            )
          } 
      
    })
  

    return(
    <div className="row">
    
        <div className="Photo">
          
            {imgs}
             {/*<img src={Img1} className="Pict"/>
            <img src={Img2} className="Pict"/>
            <img src={Img3} className="Pict"/>
            <img src={Img4} className="Pict"/>
            <img src={Img5} className="Pict"/>
            <img src={Img6} className="Pict"/>
            <img src={Img7} className="Pict"/>
            <img src={Img8} className="Pict"/>
            <img src={Img9} className="Pict"/>
            <img src={Img10} className="Pict"/>
            <img src={Img11} className="Pict"/> */}
            
        </div>
    </div>
    );
  }
  
}



export default Photo;