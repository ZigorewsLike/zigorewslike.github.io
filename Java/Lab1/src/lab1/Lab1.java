package lab1;

import java.util.*;

public class Lab1 {
    public static void main(String[] args) {
        Scanner n = new Scanner(System.in);
        int nn = n.nextInt();
        int mm = n.nextInt();
        int [][]scn = new int[mm][nn];
        for(int j=0;j<nn;j++){
        for(int i=0;i<mm;i++){
            Scanner sc = new Scanner(System.in);
            scn[i][j] = sc.nextInt();
        }
        }
        for(int j=0;j<nn;j++){
        for(int i=0;i<mm;i++){
            System.out.print(Integer.toString(scn[i][j]) + " ");
        }
        System.out.println();
        }
        
    }
    
}
