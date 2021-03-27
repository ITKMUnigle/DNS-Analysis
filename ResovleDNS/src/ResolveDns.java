import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Scanner;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import javax.net.ssl.HttpsURLConnection;

public class ResolveDns {
	private static String str;
	public static String linkIP() {		
		System.out.println("请输入需要解析的服务器:");
		Scanner sc = new Scanner(System.in);		
		str = sc.nextLine();
		String http="https://site.ip138.com/";
		String url= http+str;
		System.out.println(url);
		return url;
	}
	public static String getHtml() {
		String address=linkIP();
		String UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36";
		String result=null;
		try {
			URL url = new URL(address);
			HttpsURLConnection connection = (HttpsURLConnection)url.openConnection();
			connection.setRequestMethod("GET");
			connection.setRequestProperty("User-agent", UA);
			connection.setConnectTimeout(15000);
			connection.setReadTimeout(60000);
			connection.connect();
			int statuscode = connection.getResponseCode();
			System.out.println(statuscode);
			if (statuscode == 200) {
				BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
				String line = null;
				while ((line = reader.readLine()) != null) {
					result = result+line+"\n";
				}
			}else {
				System.out.println("状态码！= 200");
				getHtml();
			}
		} catch (Exception e) {
			// TODO: handle exception
			e.printStackTrace();
		}
		return result;
	}
	
	public static void write() {
		String filecontent =getHtml();
		File file = new File("website.txt");
		if (file.exists()) {
			file.delete();
			try {
				file.createNewFile();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}else {
			try {
				file.createNewFile();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		try {
			BufferedWriter bfw = new BufferedWriter(new FileWriter(file));
			bfw.write(filecontent);
			bfw.flush();
			bfw.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}	
	
	public static void readIP() {		
		File file = new File("website.txt");
		if (!file.exists()) {
			write();
		}
		try {
			BufferedReader bfr = new BufferedReader(new FileReader(file));
			String line = null;	
			int flag = WriteInSystem.chooseOS();
			while ((line = bfr.readLine()) !=null) {				
				if (IsIP.isNowday(line)) {					
					String line2 = bfr.readLine()+1;
					if (IsSysteminfo.isSystem(flag) ==1 ) {
						flag = 1;
						WriteInSystem.wirteInWindows(IsIP.getNowdayIP(line2), str);
					}else if (IsSysteminfo.isSystem(flag) ==2) {
						flag = 2;
						WriteInSystem.wirteInlinux(IsIP.getNowdayIP(line2), str);
					}else if(IsSysteminfo.isSystem(flag) == -1) {
						flag = -1;
						break;
					}else if(IsSysteminfo.isSystem(flag) == 0){
						flag = 0;
						readIP();
						break;
					}												
				}				
			}
			bfr.close();
		} catch (Exception e) {
			// TODO: handle exception
			e.printStackTrace();
		}
		
	}
	
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		write();
		readIP();
	}

}
class IsIP {
	//TODO 判断日期和IP
	private File file = new File("website.txt");
	private String line;
	public static boolean isNowday(String line) {
		Date date = new Date();
		//格式化时间格式
		SimpleDateFormat smd = new SimpleDateFormat("yyyy-MM-dd");
		//当前日期
		String today =smd.format(date);		
		Calendar ca = Calendar.getInstance();
		ca.setTime(date);
		ca.set(Calendar.DATE, ca.get(Calendar.DATE)-1);	
		//前一天
		String yesterday = smd.format(ca.getTime());
		//定义日期正则
		String dateregex="----[\\d+]{0,4}-[0-12](.*)-[\\d+]{0,4}";
		//判断
		try {			
			if (line !=null) {	
				Pattern p = Pattern.compile(dateregex);
				Matcher m = p.matcher(line);
				while(m.find()) {					
					String temp =m.group(0);
					if (temp.contains(today)) {
//						System.out.println("当前日期为："+temp.replaceAll("-----", ""));
						return true;
					}else if (temp.contains(yesterday)) {
//						System.out.println("无今天日期，前一天日期为："+temp.replaceAll("-----", ""));
						return true;
					}
				}
			}
		} catch (Exception e) {
			// TODO: handle exception
			e.printStackTrace();
		}	
		return false;
	}
	
	public static String getNowdayIP(String line) {
		String temp = null;
		String ipregex="((2(5[0-5]|[0-4]\\d))|[0-1]?\\d{1,2})(\\.((2(5[0-5]|[0-4]\\d))|[0-1]?\\d{1,2})){3}";
		try {			
			if (line !=null) {	
				Pattern p = Pattern.compile(ipregex);
				Matcher m = p.matcher(line);
				if(m.find()) {
					temp =m.group(0);
//					System.out.println("解析的host为："+temp);
				}
			}
		} catch (Exception e) {
			// TODO: handle exception
			e.printStackTrace();
		}
		return temp;
	}
}
class WriteInSystem {
	//TODO 写入文件
	public static int chooseOS() {
		System.out.println("请选择操作系统： 【1】Windows 【2】Linux 【0】重新输入 【默认】退出程序请输入-1");
		Scanner sc =new Scanner(System.in);
		int op;
		while((op = sc.nextInt()) != -1) {
			if (op == 1) {				
				return 1;
			}else if (op == 2) {				
				return 2;
			}else if (op == 0) {
				System.out.println("请选择操作系统： 【1】Windows 【2】Linux 【0】重新输入 【-1】退出程序");
				continue;
			}else {		
				System.out.println("请选择操作系统： 【1】Windows 【2】Linux 【0】重新输入 【-1】退出程序");
				continue;
			}
		}
		return -1;
	}
	protected static void wirteInWindows(String ip,String host) {
		System.out.println("正在写入Windows的hosts文件，请稍后……");
		File file = new File("C:\\Windows\\System32\\drivers\\etc\\hosts");
		if (!file.exists()) {
			try {
				file.createNewFile();
			    file.setExecutable(true); 
			    file.setReadable(true);
			    file.setWritable(true);
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}else {
		    file.setExecutable(true); 
		    file.setReadable(true);
		    file.setWritable(true);
		}
		
		try {
			BufferedWriter bfw = new BufferedWriter(new FileWriter(file,true));
			bfw.write("\r\n");
			bfw.write(ip+"   "+host);
			bfw.write("\r\n");
			bfw.flush();
			bfw.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		System.out.println("文件写入完成");
	}
	
	protected static void wirteInlinux(String ip,String host) {
		System.out.println("正在写入Linux的hosts文件，请稍后……");
		File file = new File("/etc/hosts");
		if (!file.exists()) {
			try {
				file.createNewFile();
			    file.setExecutable(true); 
			    file.setReadable(true);
			    file.setWritable(true);
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}else {
		    file.setExecutable(true); 
		    file.setReadable(true);
		    file.setWritable(true);
		}
		try {
			BufferedWriter bfw = new BufferedWriter(new FileWriter(file,true));
			bfw.write("\r\n");
			bfw.write(ip+"   "+host);
			bfw.write("\r\n");
			bfw.flush();
			bfw.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		System.out.println("文件写入完成");
	}
}
class IsSysteminfo{
	//TODO 判断系统类型
	protected static int isSystem(int flag) {
		while(flag != -2) {
			if (flag == getWindowinfo()) {
				flag = 1;
				return flag;
			}else if (flag == getLiunxinfo()) {
				flag = 2;
				return flag;
			}else if (flag == -1) {
				System.out.println("退出程序");
				flag = -1;
				return flag;
			}else if (flag == 0){
				flag = 0;
				return flag;
			}else {
				flag = WriteInSystem.chooseOS();
			}			
		}
		return -1;
		
	}
	private static int getWindowinfo() {
		String temp ;
		String cmd ="Systeminfo";
		Runtime run = Runtime.getRuntime();
		Process process =null;
		try {
			process=run.exec("cmd.exe /k  "+cmd);
			InputStream in = process.getInputStream();
			BufferedReader reader = new BufferedReader(new InputStreamReader(in,"GBK"));
			while ((temp =reader.readLine())!= null) {
				if (temp.contains("Microsoft Windows")) {
//					System.out.println("Windows系统");
					return 1;
				}
			}
			reader.close();
			in.close();
//			process.waitFor();
			
		} catch (Exception e) {
			// TODO: handle exception
			return 0;			
		}
		return 0;
	}
	
	private static int getLiunxinfo() {
		String temp ;
		String cmd ="uname -a";
		Runtime run = Runtime.getRuntime();
		Process process =null;
		try {
			process=run.exec(cmd);
			InputStream in = process.getInputStream();
			BufferedReader reader = new BufferedReader(new InputStreamReader(in,"UTF-8"));
			while ((temp =reader.readLine())!= null) {
				if (temp.contains("Linux")) {
//					System.out.println("Linux系统");
					return 2;				
				}
			}
			reader.close();
			in.close();
			
		} catch (Exception e) {
			// TODO: handle exception
			return 0;	
		}
		return 0;
	}
}
