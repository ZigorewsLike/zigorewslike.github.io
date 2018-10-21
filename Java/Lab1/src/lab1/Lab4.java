package lab4;

/**
 *
 * @author иго
 */
import java.util.*;
import java.io.FileReader;

public class Lab4 {
    public static void main(String[] args) throws Exception{
        FileReader file = new FileReader("C:/1.txt");
        Scanner scn = new Scanner(file);
        
        
        int i = 1;
        String []textEx = new String [4]; 
        textEx[0] = "\\chapter";
        textEx[2] = "\\section";
        textEx[1] = "\\subsection";
        textEx[3] = "\\subsubsection";
        boolean []existText = new boolean[4];
        existText[0] = false;
        existText[1] = false;
        existText[2] = false;
        existText[3] = false;
        
        
        while (scn.hasNextLine()) {
            String str = scn.nextLine();
            //System.out.println(i + " : '" + str + "' length = " + str.length());
            for(int word=0;word<4;word++){
                for(int j=0;j<str.length() - textEx[word].length();j++){
                    for(int k=0;k<textEx[word].length();k++){
                        if(textEx[word].charAt(k) == str.charAt(k+j)){
                            existText[word] = true;;
                        }else{
                            existText[word] = false;
                        }
                    }
                    int len = textEx[word].length();
                    if(existText[word]){
                        String newStr = "";
                        for(int kk = j+len+1;kk<str.length()-1;kk++){
                            newStr += str.charAt(kk);
                        }
                        System.out.println(newStr);
                        break;
                    }
                }
                 if(existText[word]){
                     break;
                 }
            }
            i++;
        }

        file.close();
    }
    
}
