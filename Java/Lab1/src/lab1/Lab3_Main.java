package lab3;

import math.isu.components.*;
public class Lab3 {
    public static void main(String[] args) {
        Button butt = new Button("Button1");
        Button butt2 = new Button("Button2");
        butt.onClick();
        butt.setWidth(50);
        butt.setHeight(7);
        butt.setCaption("Кнопка 1");
        butt.showButton();
        butt.showConfig();
        
        butt2.setLeft(0);
        butt2.setTop(0);
        butt2.setWidth(13);
        butt2.setHeight(5);
        butt2.setCaption("Butt1100000001");
        butt2.visible = false;
        butt2.showButton();
    }
}
