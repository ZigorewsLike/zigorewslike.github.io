package lab4;

/**
 *
 * @author иго
 */
import java.util.*;
import java.io.*;

public class Lab4 {
    public static void main(String[] args) throws IOException{
        System.out.println("-Введите абсолютный путь до файла.-");
        Scanner dir = new Scanner(System.in);
        System.out.println("-Куда сохранить? Введите абсолютный путь.-");
        Scanner dirW = new Scanner(System.in);
        String path = dir.nextLine();
        String pathW = dirW.nextLine();
        File myFile = new File(path);
        File myFileW = new File(pathW);
         if(!myFile.exists()){
             System.out.println("-ОШИБКА! Файл не найден!-");
         }else{
        FileReader file = new FileReader(path);
        Scanner scn = new Scanner(file);
        int i = 1;
        String []textEx = new String [4]; 
        textEx[0] = "\\chapter";
        textEx[1] = "\\section";
        textEx[2] = "\\subsection";
        textEx[3] = "\\subsubsection";
        boolean []existText = new boolean[4];
        existText[0] = false;
        existText[1] = false;
        existText[2] = false;
        existText[3] = false;
        
        System.out.println("-Результат (Вывод заголовков):-");
        FileWriter writer = new FileWriter(myFileW); 
        while (scn.hasNextLine()) {
            String str = scn.nextLine();
            //System.out.println(i + " : '" + str + "' length = " + str.length());
            for(int word=3;word>-1;word--){
                for(int j=0;j<str.length() - textEx[word].length();j++){
                    for(int k=0;k<textEx[word].length();k++){
                        if(textEx[word].charAt(k) == str.charAt(k+j)){
                            existText[word] = true;
                        }else{
                            existText[word] = false;
                        }
                    }
                    int len = textEx[word].length();
                    if(existText[word]){
                        String newStr = "";
                        for(int ii=0;ii<word+1;ii++){
                            newStr += "  ";
                            //System.out.println(word);
                        }
                        
                        for(int kk = j+len+1;kk<str.length()-1;kk++){
                            newStr += str.charAt(kk);
                        }
                        newStr += "\r";
                        writer.write(newStr);
                        writer.append('\n');
                        writer.flush();
                        System.out.println(newStr);
                        break;
                    }
                }
                 if(existText[word]){
                     existText[0] = false;
                     existText[1] = false;
                     existText[2] = false;
                     existText[3] = false;
                     break;                  
                 }
            }
            i++;
        }
        writer.close();
        file.close();
        }
    }
    
}
