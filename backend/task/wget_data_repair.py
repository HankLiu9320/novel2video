#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'qijuhong'
import os
import sys
import time
import datetime
import re
import subprocess
import multiprocessing
from configparser import ConfigParser
from HiveTask import HiveTask
ht = HiveTask()
WGET_CMD = "rsync -avLq --bwlimit=100000 --timeout=600   {} {}/{}"
REMOTE_FILE_NOT_EXISTS = "remote file {} is not exists!!!"
HDFS_PUT_CMD_LZO = "cat {local_path}/{local_file} | lzop | hadoop fs -put - {hdfs_path}/{local_file}{lzo}"
HDFS_PUT_CMD = "cat {local_path}/{local_file} | hadoop fs -put - {hdfs_path}/{local_file}"

HDFS_CREATE_LZO_INDEX = "hadoop jar $HADOOP_HOME/share/hadoop/common/lib/hadoop-lzo-0.4.20.jar " \
                        "com.hadoop.compression.lzo.DistributedLzoIndexer {hdfs_path}/{file_name}.lzo"


class WgetDataClass:
    @staticmethod
    def run_shell_cmd(shell_cmd, encoding='utf8', logger=True):
        """
        执行shell命令
        :param shell_cmd:
        :param encoding:
        :return:
        """
        res = subprocess.Popen(shell_cmd, shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        results = []
        reLogPattern = re.compile(r'^SLF4J:.*')
        while True:
            line = res.stdout.readline().decode(encoding).strip()
            if line == '' and res.poll() is not None:
                break
            elif re.match(reLogPattern, line):
                pass
            else:
                results.append(line)
                if logger:
                    ht.log.info(line)
        ReturnCode = res.returncode
        if ReturnCode != 0:
            raise Exception('\n'.join(results))
        return [ReturnCode, '\n'.join(results)]

    @staticmethod
    def run_shell_cmd_background(shell_cmd):
        try:
            subprocess.Popen(shell_cmd, shell=True)
        except Exception as e:
            ht.log.error(e)

    def check_remote_file_exists(self, remote_file):
        """
        判断服务器文件是否存在
        :param remote_file:
        :return: boolean
        """
        try:
            return os.path.exists(remote_file)
        except Exception as e:
            ht.log.error("check remote file of %s failed! Exception：%s", remote_file, e)
        return False

    def get_remote_file_size(self, remote_file):
        """
            获取服务器文件大小
        :param remote_file:
        :return:
        """
        try:
            remote_file_size = os.path.getsize(remote_file)
        except Exception as e:
            ht.log.error("get file size of %s failed! Exception：%s", remote_file, e)
            remote_file_size = -1

        return int(remote_file_size)

    def get_hdfs_file_size_and_path(self, file_name, hdfs_path, lzo):
        if lzo:
            check_file = "{file_name}.lzo".format(file_name=file_name)
        else:
            check_file = file_name
        check_cmd = "hadoop fs -ls {hdfs_path} 2>&1| grep {check_file} | awk '{{print $5,$NF}}'".format(hdfs_path=hdfs_path,
                                                                                                   check_file=check_file)
        ht.log.info("get_hdfs_file_size_and_path cmd:{}".format(check_cmd))
        cmd_ret = self.run_shell_cmd(check_cmd, logger=False)[1]
        if not cmd_ret:
            return False, 0, ''
        cmd_ret = cmd_ret.split('\n')[-1].split()
        return True, int(cmd_ret[0]), cmd_ret[1]


    def rm_hdfs_file(self, file_name, hdfs_path, lzo):
        if lzo:
            check_file = "{file_name}.lzo".format(file_name=file_name)
        else:
            check_file = file_name
        rm_cmd = "hadoop fs -rm {hdfs_path}/{check_file}*".format(hdfs_path=hdfs_path, check_file=check_file)
        ht.log.info(rm_cmd)
        try:
            self.run_shell_cmd(rm_cmd, logger=False)
        except:
            pass

    def is_hdfs_file_exists_or_uploading(self, file_name, hdfs_path, lzo):
        hdfs_file_size_path = self.get_hdfs_file_size_and_path(file_name, hdfs_path, lzo)
        if not hdfs_file_size_path[0]:
            return False

        size = hdfs_file_size_path[1]
        if '_COPYING_' in hdfs_file_size_path[2]:
            time.sleep(30)
            hdfs_file_size_path = self.get_hdfs_file_size_and_path(file_name, hdfs_path, lzo)
            size_new = hdfs_file_size_path[1]
            if size_new > size or (size_new == size and '_COPYING_' not in hdfs_file_size_path[2]):
                return True
            else:
                self.rm_hdfs_file(file_name, hdfs_path, lzo)
                return False
        else:
            return True

    def is_hdfs_path_exists(self, path):
        checkHDFSPathExists = "hdfs dfs -test -e " + path + "; echo $?"
        status = self.run_shell_cmd(checkHDFSPathExists)
        if status[1] == '0':
            return True
        else:
            return False

    def mkdir_hdfs_path(self, path):
        mkdir_cmd = "hadoop fs -mkdir -p {}".format(path)
        try:
            self.run_shell_cmd(mkdir_cmd)
        except:
            pass

    def create_lzo_index(self, hdfs_path, file_name):
        create_cmd = HDFS_CREATE_LZO_INDEX.format(hdfs_path=hdfs_path, file_name=file_name)
        ht.log.info(create_cmd)
        self.run_shell_cmd_background(create_cmd)

    def put_file_to_hdfs(self, local_path, local_file, hdfs_path, lzo):
        """
        :param local_path:
        :param local_file:
        :param hdfs_path:
        :param lzo:
        :return:
        """
        if not self.is_hdfs_path_exists(hdfs_path):
            self.mkdir_hdfs_path(hdfs_path)

        if self.is_hdfs_file_exists_or_uploading(file_name=local_file, hdfs_path=hdfs_path, lzo=lzo):
            ht.log.info("hdfs file {}/{} is already exists or is uploading".format(hdfs_path, local_file))
            return

        if lzo:
            exec_put_cmd = HDFS_PUT_CMD_LZO.format(local_path=local_path,
                                               local_file=local_file,
                                               hdfs_path=hdfs_path,
                                               lzo=".lzo")
        else:
            exec_put_cmd = HDFS_PUT_CMD.format(local_path=local_path,
                                               local_file=local_file,
                                               hdfs_path=hdfs_path)
        ht.log.info(exec_put_cmd)
        retry_counts = 0
        while retry_counts < 2:
            try:
                self.run_shell_cmd(exec_put_cmd)
                ht.log.info('file {} put to hdfs successfully'.format(local_file))
                break
            except Exception as e:
                retry_counts += 1
                ht.log.error('file {} put to hdfs error !!!'.format(local_file))
                time.sleep(60)
                if self.is_hdfs_file_exists_or_uploading(local_file, hdfs_path, lzo):
                    ht.log.info("hdfs file {}/{} is uploading".format(hdfs_path, local_file))

                    return
        if retry_counts >= 2:
            ht.log.error('file {} total put {} times ,exceed peak value'.format(local_file, hdfs_path))
            raise Exception('file {} put to hdfs error !!!'.format(local_file))


    def check_wget_file(self, remote_file, local_file):
        local_file_size = os.path.getsize(local_file)
        remote_file_size = self.get_remote_file_size(remote_file)
        ht.log.info("remote_file %s size: %d", remote_file, remote_file_size)
        ht.log.info("local_file %s size: %d", local_file, local_file_size)
        return remote_file_size == local_file_size

    def wget_put_one_file(self, ip, data_day_str, data_day, data_hour, server_file, server_final_file,
                          local_path, local_file, hdfs_path, put_hdfs=True, lzo=True):
        """
            单文件下载
        :param ip: ip
        :param data_day_str: 日期参数 2016-03-12
        :param data_day: 日期参数 20160312
        :param data_hour: 小时 17
        :param data_ten_min: 十分钟 0-5
        :param server_file: 服务器文件路径
        :param server_final_file: 服务器小时文件路径
        :param local_path: 本地路径
        :param local_file: 本地文件名
        :return:
        """
        data_yesterday = str(datetime.datetime.strptime(data_day_str, "%Y-%m-%d").date()-datetime.timedelta(days=1))

        server_file = server_file.format(ip=ip)
        server_final_file = server_final_file.format(ip=ip, data_day=data_day, data_hour='00')
        local_path = local_path.format(data_day_str=data_yesterday)
        local_file = local_file.format(ip=ip, data_day=data_day, data_hour=data_hour)
        hdfs_path = hdfs_path.format(data_day_str=data_yesterday, data_hour='23')

        wget_server_file_cmd = WGET_CMD.format(server_file, local_path, local_file)
        wget_server_final_file_cmd = WGET_CMD.format(server_final_file, local_path, local_file)


        try:
            if not os.path.isdir(local_path):
                os.makedirs(local_path)
        except:
            pass

        while True:
            current_time_str = datetime.datetime.now().strftime('%Y%m%d%H%M')
            ht.log.info("ip:{}, time:{}".format(ip, current_time_str))
            current_date = current_time_str[0:8]
            current_hour = current_time_str[8:10]
            current_min = int(current_time_str[10:12])
            try:
                if current_date == data_day and current_hour == '00' and current_min < 50:
                    if self.check_remote_file_exists(server_file):
                        ht.log.info(wget_server_file_cmd)
                        self.run_shell_cmd(wget_server_file_cmd)
                elif current_date == data_day and current_hour == '00' and current_min >= 50:
                    time.sleep(15*60)
                    continue
                else:
                    if self.check_remote_file_exists(server_final_file):
                        ht.log.info(wget_server_final_file_cmd)
                        self.run_shell_cmd(wget_server_final_file_cmd)
                if put_hdfs:
                    self.put_file_to_hdfs(local_path, local_file, hdfs_path, lzo)
                break
            except:
                pass

    def wget_put_files(self, ip_list, data_day_str, data_day, data_hour, server_file, server_final_file,
                       local_path, local_file, hdfs_path, put_hdfs=True, lzo=True):
        process_list = []
        for ip in ip_list:
            process_list.append(multiprocessing.Process(target=self.wget_put_one_file,
                                                        args=(ip, data_day_str, data_day, data_hour,
                                                              server_file, server_final_file, local_path, local_file,
                                                              hdfs_path, put_hdfs, lzo)))
        for p in process_list:
            p.daemon = True
            p.start()
        for p in process_list:
            p.join()

    def get_conf_file_from_hdfs(self, business_file):
        """
            下载配置文件到本地
        :return:
        """
        hdfs_file = "/user/jdw_traffic/lib_dat/wget_data_conf/cfs/" + business_file
        if os.path.exists(business_file):
            os.remove(business_file)
        get_file_from_hdfs_cmd = "hadoop fs -get {} {}".format(hdfs_file, business_file)
        ht.log.info(get_file_from_hdfs_cmd)
        try:
            self.run_shell_cmd(get_file_from_hdfs_cmd)
        except:
            raise "配置文件不存在，请检查业务参数是否正确！"

    def touch_success(self, hdfs_path, data_day_str, data_day, data_hour, all_job_count, job_index):
        hdfs_path = hdfs_path.format(data_day_str=data_day_str, data_day=data_day, data_hour=data_hour)
        #hdfs_parent_path = hdfs_path[:hdfs_path.rfind('/')]

        if not self.is_hdfs_path_exists(hdfs_path):
            pass
        else:
            touch_job_success_cmd = "hadoop fs -touchz {}/{}_success".format(hdfs_path, job_index)
            ht.log.info(touch_job_success_cmd)
            self.run_shell_cmd(touch_job_success_cmd)


    def rm_local_file_days_before(self, local_main_path, days):
        cmd = "find {path} -maxdepth 1 -mtime +{days} -type d  -exec /bin/rm -rf {{}} \\; ".format(path=local_main_path, days=days)
        ht.log.info(cmd)
        try:
            self.run_shell_cmd_background(cmd)
        except:
            pass

    def get_ip_list(self, business, data_day, data_hour, cfs):
        ip_file_name = business + "_" + data_day + data_hour
        ip_file_dir = os.path.join(business, str(os.getpid()))
        ip_url = cfs + "jazz/" + business + "/" + ip_file_name
        ip_list_cmd = "rsync -avPLq {} {}/{}".format(ip_url, ip_file_dir, ip_file_name)

        try:
            print(os.getcwd())
            if not os.path.exists(ip_file_dir):
                os.makedirs(ip_file_dir)

            if os.path.exists(ip_file_dir + "/" + ip_file_name):
                os.remove(ip_file_dir + "/" + ip_file_name)

            self.run_shell_cmd(ip_list_cmd)

            ip_list = []
            with open(ip_file_dir + "/" + ip_file_name, 'r') as fw:
                line = fw.readline()
                while line:
                    if line.strip() != '':
                        ip_list.append(line.strip())
                    line = fw.readline()
        except Exception as e:
            raise Exception(Exception("获取ip列表文件失败！！"), e)

        import shutil

        if os.path.exists(ip_file_dir):
            shutil.rmtree(ip_file_dir)

        ip_list = list(set(ip_list))
        print(ip_list)

        return ip_list

def main():
    if len(sys.argv) < 2:
        print("""usage: python3 wget_data.py date_hour business all_job_count job_index""")
        sys.exit(-1)
    ht.log.info(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    time_str = sys.argv[1].replace('-', '').replace(' ', '').replace(':', '')
    business = sys.argv[2]
    if len(sys.argv) >= 4:
        all_job_count = int(sys.argv[3])
        job_index = int(sys.argv[4])
    else:
        all_job_count = 1
        job_index = 0

    data_day = ''.join([time_str[0:4], time_str[4:6], time_str[6:8]])
    data_day_str = '-'.join([time_str[0:4], time_str[4:6], time_str[6:8]])
    data_hour = time_str[8:10]
    data_ten_min = ''  # 按小时下载，此参数值赋为空

    wget_data = WgetDataClass()
    wget_data.get_conf_file_from_hdfs(business + ".properties")
    # ip_list = wget_data.get_ip_list(business, data_day, data_hour)

    cf = ConfigParser()
    cf.read(business + ".properties")
    if business not in cf.sections():
        ht.log.error('业务不正确！！！！')
        ht.log.info('配置文件有如下配置：{}', cf.sections())
        raise '业务不正确'

    cfs = cf.get(business, 'cfs')
    server_file = cfs + cf.get(business, 'server_file')
    server_final_file = cfs + cf.get(business, 'server_final_file')
    local_main_path = cf.get(business, 'local_main_path')
    local_day_path = cf.get(business, 'local_day_path')
    local_path = local_main_path + os.path.sep + local_day_path
    local_file = cf.get(business, 'local_file')
    local_file_repair = local_file + "_repair"
    hdfs_path = cf.get(business, 'hdfs_path')
    put_hdfs = cf.getboolean(business, 'put_hdfs')
    lzo = cf.getboolean(business, 'lzo')

    # 分散抽取列表
    sub_ip_list = []
    ip_list_array = wget_data.get_ip_list(business, data_day, data_hour, cfs)
    for i in range(len(ip_list_array)):
        if i % all_job_count == job_index:
            sub_ip_list.append(ip_list_array[i].strip())
    if len(sub_ip_list) == 0:
        ht.log.info("下载任务编号错误， all_job_count:%d, job_index:%d", all_job_count, job_index)
        sys.exit(0)

    wget_data.wget_put_files(sub_ip_list, data_day_str, data_day, data_hour, server_file, server_final_file,
                             local_path, local_file_repair, hdfs_path,  put_hdfs, lzo)
    # if touch_success:
    #     wget_data.touch_success(hdfs_path, data_day_str, data_day, data_hour, all_job_count, job_index)

    wget_data.rm_local_file_days_before(local_main_path, 1)
    ht.log.info("SUCCESS! all files OK.")


if __name__ == '__main__':
    main()
