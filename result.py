from robot.api import ExecutionResult
import sys
import JSON_markdown_result
import json
import pandas
import os
import datetime

#=========================== Global variables =========================
# Json & markdown output files path
result_log_path = os.path.join(os.getcwd(), "Json_Markdown_Logs")
time_stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
json_result_file = os.path.join(result_log_path, "result_totalStat"+time_stamp+".json")


# sys.argv[1] is the path to the output.xml file from Post-Merge 
# sys.argv[2] is the path to the output.xml file from Daily-Merge
post_merge_outputfile = sys.argv[1]
Daily_merge_outputfile = sys.argv[2]

#=======================================================================

# create a json & markdown for Post-Merge & daily-Merge
for i in sys.argv[1:]:
    print(i, file=sys.stdout)
    result = ExecutionResult(i)
    stats = result.statistics

    #create a dictionary to store the total statistics
    stats_dict = {
        "Total number of Tests": stats.total.total,
        "Passed Tests": stats.total.passed,
        "Failed Tests": stats.total.failed,
        "Skipped Tests": stats.total.skipped
    }

    # Create a json file
    with open(json_result_file, "a") as f:
        json.dump(stats_dict, f, indent=4) 


    # Create a markdown file
    df = pandas.DataFrame.from_dict(stats_dict, orient='index', columns=['Total Statistics'])
    df.reset_index(inplace=True)
    if 'PostMerge' in i:
        markdown_file = os.path.join(result_log_path, "PostMerge_totalStat"+time_stamp+".md")
        df.rename(columns={'index': 'Post-Merge'}, inplace=True)
        df.to_markdown(index=False, tablefmt='fancy_grid', buf=markdown_file)
    elif 'Daily' in i:
        markdown_file = os.path.join(result_log_path, "DailyMerge_totalStat"+time_stamp+".md")
        df.rename(columns={'index': 'Daily-Merge'}, inplace=True)
        df.to_markdown(index=False, tablefmt='fancy_grid', buf=markdown_file)
    else:
        df.rename(columns={'index': 'installation'}, inplace=True)
    

