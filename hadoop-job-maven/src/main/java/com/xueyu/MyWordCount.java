package com.xueyu;

import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
//import org.apache.hadoop.mapred.FileOutputFormat;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;




public class MyWordCount {
	
	public static class TokenizerMapper
		extends Mapper<Object, Text, Text, IntWritable> {
		private final static IntWritable one = new IntWritable(1);
		private Text word = new Text();
		
		public void map(Object key, Text value, Context context)
			throws IOException, InterruptedException
		{
			StringTokenizer itr = new StringTokenizer(value.toString());
			while (itr.hasMoreTokens()) {
				word.set(itr.nextToken());
				context.write(word, one);
			}
		}
	}
	
	public static class IntSumReducer
		extends Reducer<Text, IntWritable, Text, IntWritable> {
		private IntWritable result = new IntWritable();
		
		public void reduce(Text key, Iterable<IntWritable> values, 
				 				Context context) 
				 				throws IOException, InterruptedException {
			int sum = 0;
			for (IntWritable val : values) {
				sum += val.get();
			}
			result.set(sum);
			context.write(key, result);
			
			
		}

	}

	public static void main(String[] args) throws Exception {
		// TODO Auto-generated method stub
		Configuration conf = new Configuration();
                String[] otherargs = new GenericOptionsParser(conf, args).getRemainingArgs();
		
		Job job = new Job(conf, "mywordcount");
		//job.setJarByClass(MyWordCount.class);
		job.setJar("/root/xueyu/myhadoop/tmp5/htry.jar");
		job.setMapperClass(TokenizerMapper.class);
		job.setReducerClass(IntSumReducer.class);
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(IntWritable.class);
		FileInputFormat.addInputPath(job, new Path(otherargs[0]));
		FileOutputFormat.setOutputPath(job, new Path(otherargs[1]));
		
		System.exit(job.waitForCompletion(true) ? 0 : 1);
		
		
		
		
		

	}

}
