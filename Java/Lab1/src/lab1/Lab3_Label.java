package math.isu.components;

import java.util.Objects;

public class Label {
    String text_align;
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
    int textTop = 1;
    int textLeft = 1;
    int tag;
    String color;
    
    public void showConfig(){
        for(int i=0;i<this.left;i++){
                    System.out.print(" ");
        }
        System.out.println("Left = "+this.left+"; Top = "+this.top+"; Width = "+this.width+"; Height = "+this.height+"; Name = "+this.name+"; Color="+this.color+"; Text = "+this.caption+"; Text-align="+this.text_align);
        System.out.println();
    }
    
    public void setWidth(int width){
        if(width > (this.caption).length()){
            this.width = width*2;
        }else{
            this.width = (this.caption).length()*2;
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
    
    public void setTextAlign(String align){
        switch(align){
            case "a_center":
                textTop = this.height / 2;
                textLeft = ((this.width / 2) - ((this.caption).length()));
                break;
            case "a_left":
                textLeft = 1;
                break;
            case "a_right":
                textLeft = ((this.width) - ((this.caption).length()+1));
                break;
            case "a_top":
                textTop = 1;
                break;
            case "a_bottom":
                textTop = this.height-2;
                break;
            case "a_top_center":
                textTop = this.height / 2;
                break;
            case "a_top_left":
                textLeft = ((this.width / 2) - ((this.caption).length()));
                break;
            case "a_none":
                textLeft = 1;
                textTop = 1;
                break;
            default:
                textTop = this.height / 2;
                textLeft = ((this.width / 2) - ((this.caption).length()));
                break;
        }
    }
    
    
    public void showLabel(){
        if(this.visible){
                
        for(int t=0;t<this.top;t++){
                    System.out.println();
                }
        for(int j=0;j<this.height;j++){
            for(int l=0;l<this.left;l++){
                    System.out.print(" ");
            }
            for(int i=0;i<this.width;i++){
                if((j==0) || (j==this.height-1)){
                    System.out.print(" ");
                }else if(((i==0)||(i==this.width-1)) && (j != textTop)){
                    System.out.print(" ");
                }else if(((i==0)||(i==this.width-((this.caption).length()*2))) && (j == textTop)){
                    System.out.print(" ");
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
    
    public Label(String name){
        this.name = name;
        this.caption = name;
        this.left = 0;
        this.top = 0;
        this.width = (this.caption).length()*2;
        this.height = 3;
        this.color = "c_black";
        this.visible = true;
        this.text_align = "a_center";
    }
    public Label(String name,int left,int top){
        this.name = name;
        this.caption = name;
        this.left = left;
        this.top = top;
        this.width = (this.caption).length()*2;
        this.height = 3;
        this.color = "c_black";
        this.visible = true;
        this.text_align = "a_center";
    }
    
    public Label(String name,int left,int top,int width,int height){
        this.name = name;
        this.caption = name;
        this.left = left;
        this.top = top;
        this.width = width;
        this.height = height;
        this.color = "c_black";
        this.visible = true;
        this.text_align = "a_center";
    }
    public Label(String name,int left,int top,int width,int height,String color){
        this.name = name;
        this.caption = name;
        this.left = left;
        this.top = top;
        this.width = width;
        this.height = height;
        this.visible = true;
        this.text_align = "a_center";
        this.color = color;
    }
    
    @Override
    public String toString() {
        return "Label [LabelLeft=" + Label.this.left 
                + ", LabelTop=" + Label.this.top 
                + ", LabelName=" + Label.this.name
                + ", LabelCaptiont=" + Label.this.caption 
                + ", LabelWidth=" + Label.this.width
                + ", LabelHeight=" + Label.this.height
                + ", LabelTag=" + Label.this.tag
                + ", LabelVisible=" + Label.this.visible
                + ", LabelColor=" + Label.this.color
                + ", LabelTextAlign=" + Label.this.text_align 
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
        Label q = (Label) obj;
        return (name.equals(q.name) 
                && (left == q.left) 
                && (top == q.top) 
                && (width == q.width) 
                && (height == q.height) 
                && (tag == q.tag) 
                && (caption.equals(q.caption)) 
                && (color.equals(q.color))
                && (text_align.equals(q.text_align)) 
                && (visible == q.visible)
                && (enabled == q.enabled)
                );
        
    }

    @Override
    public int hashCode() {
        int hash = 3;
        hash = 89 * hash + this.left;
        hash = 89 * hash + this.top;
        hash = 89 * hash + this.width;
        hash = 89 * hash + this.height;
        hash = 89 * hash + Objects.hashCode(this.caption);
        hash = 89 * hash + Objects.hashCode(this.name);
        hash = 89 * hash + (this.enabled ? 1 : 0);
        hash = 89 * hash + (this.visible ? 1 : 0);
        hash = 89 * hash + this.tag;
        hash = 89 * hash + Objects.hashCode(this.color);
        hash = 89 * hash + Objects.hashCode(this.text_align);
        return hash;
    }
}
