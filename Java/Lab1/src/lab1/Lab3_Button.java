package math.isu.components;

import java.util.Objects;

public class Button {
    public int left;
    public int top;
    int width;
    int height;
    public String caption;
    char symbolOne = '-';
    char symbolTwo = '|';
    public String name;
    public boolean enabled;
    public boolean visible;
    int tag;
    public void onClick(){
        System.out.println("Click!");
    }
    public void setStyle(char cr){
        symbolOne = cr;
        symbolTwo = cr;
    }
    public void setStyle(char cr,char cr2){
        symbolOne = cr;
        symbolTwo = cr2;
    }
    public void setStyle(){
        symbolOne = '-';
        symbolTwo = '|';
    }
    public void setWidth(int width){
        if(width > (this.caption).length()/2){
            this.width = width;
        }else{
            this.width = (this.caption).length()/2+1;
        }
    }
    public void setHeight(int height){
        if(height > 2){
            this.height = height;
        }else{
            this.height = 3;
        }
    }
    public int getWidth(){
        return (this.width);
    }
    public int getHeight(){
        return (this.height);
    }
    public void setLeft(int left){
        if(left >= 0){
            this.left = left;
        }else{
            this.left = 0;
        }
    }
    public void setTop(int top){
        if(top >= 0){
            this.top = top;
        }else{
            this.top = 0;
        }
    }
    public int getLeft(){
        return (this.left);
    }
    public int getTop(){
        return (this.top);
    }
    public void showConfig(){
        for(int i=0;i<this.left;i++){
                    System.out.print(" ");
        }
        System.out.println("Left = "+this.left+"; Top = "+this.top+"; Width = "+this.width+"; Height = "+this.height+"; Name = "+this.name+"; Text = "+this.caption);
        System.out.println();
    }
    public void showButton(){
        if(this.visible){
        int textTop = this.height / 2;
        int textLeft = ((this.width*2 / 2) - ((this.caption).length()/2));
        for(int t=0;t<this.top;t++){
                    System.out.println();
                }
        for(int j=0;j<this.height;j++){
            for(int l=0;l<this.left;l++){
                    System.out.print(" ");
            }
            for(int i=0;i<this.width*2;i++){
                if((j==0) || (j==this.height-1)){
                    System.out.print(symbolOne);
                }else if(((i==0)||(i==this.width*2-1)) && (j != textTop)){
                    System.out.print(symbolTwo);
                }else if(((i==0)||(i==this.width*2-((this.caption).length()))) && (j == textTop)){
                    System.out.print(symbolTwo);
                }else if((j == textTop) && (i == textLeft)){
                    System.out.print(this.caption);
                }else{
                    System.out.print(" ");
                }
            }
            System.out.println();
        }
        System.out.println("");
        }
    }
    public Button(String name){
        this.name = name;
        this.caption = name;
        this.left = 0;
        this.top = 0;
        this.width = 13;
        this.height = 5;
        this.visible = true;
    }
    
    public Button(String name,int left,int top){
        this.name = name;
        this.caption = name;
        this.left = left;
        this.top = top;
        this.width = 13;
        this.height = 5;
        this.visible = true;
    }
    
    public Button(String name,int left,int top,int width,int height){
        this.name = name;
        this.caption = name;
        this.left = left;
        this.top = top;
        this.width = width;
        this.height = height;
        this.visible = true;
    }
    public Button(String name,int left,int top,int width,int height,char symbolOne){
        this.name = name;
        this.caption = name;
        this.left = left;
        this.top = top;
        this.width = width;
        this.height = height;
        this.visible = true;
        this.symbolOne = symbolOne;
        this.symbolTwo = symbolOne;
    }
    public Button(String name,int left,int top,int width,int height,char symbolOne,char symbolTwo){
        this.name = name;
        this.caption = name;
        this.left = left;
        this.top = top;
        this.width = width;
        this.height = height;
        this.visible = true;
        this.symbolOne = symbolOne;
        this.symbolTwo = symbolTwo;
    }
    public Button(String name,String caption){
        this.name = name;
        this.caption = caption;
        this.left = 0;
        this.top = 0;
        this.width = 13;
        this.height = 5;
        this.visible = true;
    }
    public Button(String name,String caption,int left,int top){
        this.name = name;
        this.caption = caption;
        this.left = left;
        this.top = top;
        this.width = 13;
        this.height = 5;
        this.visible = true;
    }
    
    public Button(String name,String caption,int left,int top,int width,int height){
        this.name = name;
        this.caption = caption;
        this.left = left;
        this.top = top;
        this.width = width;
        this.height = height;
        this.visible = true;
    }
    public Button(String name,String caption,int left,int top,int width,int height,char symbolOne){
        this.name = name;
        this.caption = caption;
        this.left = left;
        this.top = top;
        this.width = width;
        this.height = height;
        this.visible = true;
        this.symbolOne = symbolOne;
        this.symbolTwo = symbolOne;
    }
    public Button(String name,String caption,int left,int top,int width,int height,char symbolOne,char symbolTwo){
        this.name = name;
        this.caption = caption;
        this.left = left;
        this.top = top;
        this.width = width;
        this.height = height;
        this.visible = true;
        this.symbolOne = symbolOne;
        this.symbolTwo = symbolTwo;
    }
    
    @Override
    public String toString() {
        return "Button [ButtonLeft=" + Button.this.left 
                + ", ButtonTop=" + Button.this.top 
                + ", ButtonName=" + Button.this.name
                + ", ButtonCaptiont=" + Button.this.caption 
                + ", ButtonWidth=" + Button.this.width
                + ", ButtonHeight=" + Button.this.height
                + ", ButtonTag=" + Button.this.tag
                + ", ButtonVisible=" + Button.this.visible
                + "]";
    }
    @Override
    public boolean equals(Object obj) {
        if(obj == this){
            return true;    
        }
        if(obj == null || obj.getClass() != this.getClass()){
            return false;
        }
        Button q = (Button) obj;
        return (name.equals(q.name) 
                && (left == q.left) 
                && (top == q.top) 
                && (width == q.width) 
                && (height == q.height) 
                && (tag == q.tag) 
                && (caption.equals(q.caption)) 
                && (visible == q.visible)
                && (enabled == q.enabled)
                );
        
    }

    @Override
    public int hashCode() {
        int hash = 3;
        hash = 79 * hash + this.left;
        hash = 79 * hash + this.top;
        hash = 79 * hash + this.width;
        hash = 79 * hash + this.height;
        hash = 79 * hash + Objects.hashCode(this.caption);
        hash = 79 * hash + Objects.hashCode(this.name);
        hash = 79 * hash + (this.enabled ? 1 : 0);
        hash = 79 * hash + (this.visible ? 1 : 0);
        hash = 79 * hash + this.tag;
        return hash;
    }
}
