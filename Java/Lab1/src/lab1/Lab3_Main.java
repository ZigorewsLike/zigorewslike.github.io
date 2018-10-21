package lab3;

import math.isu.components.*;
public class Lab3 {
    public static void main(String[] args) {
        Button butt = new Button("Button1","Кнопка 1");
        Button butt2 = new Button("Button2",5,0,18,5,'+');
        Button butt3 = new Button("Button3",50,2);
        Button butt4 = new Button("Button4","Кнопка 4",9,7,35,7,'4');
        Label lab = new Label("Label1");
        
        lab.caption = "Labellll";
        lab.setWidth(90);
        lab.setHeight(9);
        lab.setLeft(0);
        lab.showLabel();
        lab.showConfig();
        
        butt.onClick();
        butt.setWidth(90);
        butt.setHeight(7);
        butt.setLeft(10);
        butt.setTop(2);
        butt.setStyle('*');
        butt.showButton();
        butt.showConfig();
        
        butt2.caption = "Кнопка 2";
        butt2.showButton();
        butt2.showConfig();
        
        butt3.caption = "Кнопка 3";
        butt3.showButton();
        butt3.showConfig();
        
        butt4.showButton();
        butt4.showConfig();
        
        System.out.println(butt.toString());
    }
}
