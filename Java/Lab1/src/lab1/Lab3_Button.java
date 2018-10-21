package math.isu.components;
public class Button {
    String align;
    public int left;
    public int top;
    int width;
    int height;
    String caption;
    String name;
    public boolean enabled;
    public boolean visible;
    int tag;
    public void onClick(){
        System.out.println("Click!");
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
    public void showConfig(){
        for(int left=0;left<this.left;left++){
                    System.out.print(" ");
        }
        System.out.println("Left = "+this.left+"; Top = "+this.top+"; Width = "+this.width+"; Height = "+this.height+"; Name = "+this.name+"; Text = "+this.caption);
        System.out.println();
    }
    public void showButton(){
        if(this.visible){
        int textTop = this.height / 2;
        int textLeft = ((this.width*2 / 2) - ((this.caption).length()/2));
        for(int top=0;top<this.top;top++){
                    System.out.println();
                }
        for(int j=0;j<this.height;j++){
            for(int left=0;left<this.left;left++){
                    System.out.print(" ");
            }
            for(int i=0;i<this.width*2;i++){
                if((j==0) || (j==this.height-1)){
                    System.out.print("-");
                }else if(((i==0)||(i==this.width*2-1)) && (j != textTop)){
                    System.out.print("|");
                }else if(((i==0)||(i==this.width*2-((this.caption).length()))) && (j == textTop)){
                    System.out.print("|");
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
    public void setCaption(String caption){
        this.caption = caption;
    }
    
    public Button(String name){
        this.name = name;
        this.caption = name;
        this.left = 10;
        this.top = 2;
        this.width = 13;
        this.height = 5;
        this.visible = true;
    }
    
}
