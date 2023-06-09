import sys
import os,read
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMessageBox,QDialog
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QScrollArea, QLabel, QLineEdit, QPushButton, QSplitter
from PyQt5.QtCore import QSettings,Qt
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5 import QtCore
import analyze
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QProgressDialog
from PyQt5.QtCore import Qt, QThreadPool, QTimer
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QMenu, QAction, QApplication
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
from functools import partial
from PyQt5.QtWidgets import QTextBrowser, QHBoxLayout, QVBoxLayout, QDialog



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.search_thread = None
        self.search_worker = analyze.SearchWorker([],'')
        self.search_worker.signals.search_completed.connect(self.handle_search_completed)
        self.config_cheak()


        # 设置窗口大小
        self.setGeometry(100, 100, 900, 600)
        self.setFixedSize(self.size())  # 锁定窗口大小

        # 创建菜单栏
        menubar = self.menuBar()

        # 创建文件菜单
        file_menu = menubar.addMenu("文件")
        folder_action = QAction("选择文件夹", self)
        folder_action.triggered.connect(self.select_folder)
        file_menu.addAction(folder_action)

        # 创建搜索菜单
        search_menu = menubar.addMenu("搜索")
        search_action = QAction("关键词搜索", self)
        search_menu.addAction(search_action)

        # 创建帮助菜单
        help_menu = menubar.addMenu("帮助")
        help_action = QAction("查看帮助", self)
        help_menu.addAction(help_action)

        # 创建主窗口的中心部件
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # 创建上方区域的部件
        self.top_widget = QWidget(central_widget)
        self.top_widget.setGeometry(20, 10, self.width(), self.height() // 6+10)

        # 创建上方区域的部件
        self.label_widget = QLabel(self.top_widget)
        self.label_widget.setGeometry(10, 10, self.top_widget.width()-180, 60)
        self.label_widget.setAlignment(Qt.AlignCenter)
        self.label_widget.setStyleSheet("QLabel { border: 1px solid black; }")
        self.label_widget.setWordWrap(True)  # 启用自动换行
        self.update_folder_path()

        self.button_path = QPushButton("修改", self.top_widget)
        self.button_path.setGeometry(self.top_widget.width()-158,8, 104, 64)
        self.button_path.clicked.connect(folder_action.trigger)

        # 创建下方区域的部件
        self.bottom_widget = QWidget(central_widget)
        self.bottom_widget.setGeometry(20, self.height() // 6 - 10, self.width() - 20, self.height() * 5 // 6 - 30)

        # 添加文件列表部件到下方区域
        
        self.file_list_widget = QScrollArea(self.bottom_widget)
        self.file_list_widget.setGeometry(10, 0, 400, self.bottom_widget.height() - 20)

        self.file_list_label_widget = QWidget(self.file_list_widget)
        self.file_list_label_layout = QVBoxLayout(self.file_list_label_widget)
        self.file_list_label_layout.setContentsMargins(0, 0, 0, 0)

        self.file_list_label = QLabel(self.file_list_label_print())
        self.file_list_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.file_list_label_layout.addWidget(self.file_list_label)
        self.file_list_widget.setWidget(self.file_list_label_widget)

        # 添加文本输入框和按钮到右侧区域
        self.text_input1 = QLineEdit(self.bottom_widget)
        self.button1 = QPushButton("AND", self.bottom_widget)
        self.text_input2 = QLineEdit(self.bottom_widget)
        self.button2 = QPushButton("AND", self.bottom_widget)
        self.text_input3 = QLineEdit(self.bottom_widget)
        self.button3 = QPushButton("搜索", self.bottom_widget)
        self.button4 = QPushButton("重置", self.bottom_widget)

        # 设置部件的位置和大小
        self.text_input1.setGeometry(420, 0, self.bottom_widget.width() - 450, 60)
        self.button1.setGeometry(420, 70, 100, 60)
        self.text_input2.setGeometry(520, 70, self.bottom_widget.width() - 550, 60)
        self.button2.setGeometry(420, 140, 100, 60)
        self.text_input3.setGeometry(520, 140, self.bottom_widget.width() - 550, 60)
        self.button3.setGeometry(635, 210, 215, 60)
        self.button4.setGeometry(420, 210, 215, 60)
        
        #设置各个部件功能
        # 按钮1点击事件
        self.button1.clicked.connect(self.toggle_button1)
        # 按钮2点击事件
        self.button2.clicked.connect(self.toggle_button2)
        # 搜索按钮点击事件
        self.button3.clicked.connect(self.generate_new_page)
        # 重置按钮点击事件
        self.button4.clicked.connect(self.reset_inputs)

#这里开始为文件路径相关方法
    def path_cheak(self):
        self.config = QSettings("config.ini", QSettings.IniFormat)
        folder_path = self.config.value("folder_path")
        if folder_path is None or folder_path == "":
            return False
        else:
            return True
    
    def get_path(self):
        self.config = QSettings("config.ini", QSettings.IniFormat)
        folder_path = self.config.value("folder_path")
        return folder_path

    def config_cheak(self):
        # 解析配置文件
        self.config = QSettings("config.ini", QSettings.IniFormat)
        folder_path = self.config.value("folder_path")
        if folder_path is None or folder_path == "":
            reply = QMessageBox.question(self, "文件夹路径未设置", "文件夹路径未设置，是否前往设置？", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.select_folder_first()
        else:
            self.folder_path = folder_path

    def select_folder_first(self):
        # 实现选择文件夹的逻辑
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", options=QFileDialog.ShowDirsOnly)
        if folder_path:
            self.folder_path = folder_path
            self.config.setValue("folder_path", folder_path)
    
    def update_folder_path(self):
        self.label_widget.setText(f"当前文件夹位置: {self.folder_path}")

    def select_folder(self):
        # 实现选择文件夹的逻辑
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", options=QFileDialog.ShowDirsOnly)
        if folder_path:
            self.folder_path = folder_path
            self.config.setValue("folder_path", folder_path)
            self.update_folder_path()  # 更新 label_widget 的文本内容
            self.update_files()
    
    def update_folder_path(self):
        self.label_widget.setText(f"当前文件夹位置: {self.folder_path}")

#这里开始为更新文件夹内文件内容字符串
    def set_files(self):
        self.file_list_label = QLabel(self.file_list_label_print(), self.bottom_widget)
        
    def update_files(self):    
        new_text = self.file_list_label_print()
        self.file_list_label.setText(new_text)
        
    def file_list_label_print(self):
        try:
            list_files = read.sort_files(read.get_file_names(self.get_path()))
        except FileNotFoundError:
            self.select_folder_first()
        list_files = read.sort_files(read.get_file_names(self.get_path()))
        string = ""
        for list_file in list_files:
            string = string + list_file + "\n"
        return string 

#这里开始为搜索框按钮功能方法
    def reset_inputs(self):
        self.text_input1.clear()
        self.text_input2.clear()
        self.text_input3.clear()
        print('reset')

    '''
    def generate_new_page(self):
        # 创建搜索中对话框
        progress_dialog = QMessageBox(self)
        progress_dialog.setWindowTitle("搜索中")
        progress_dialog.setText("请稍后...")
        progress_dialog.setStandardButtons(QMessageBox.NoButton)
        progress_dialog.show()
        print('dialog')
        input1 = self.text_input1.text()
        input2 = self.text_input2.text()
        input3 = self.text_input3.text()
        if self.button1.text() == "AND":
            button1_state = True
        else:
            button1_state = False
        if self.button2.text() == "AND":
            button2_state = True
        else:
            button2_state = False
        search_list = [[input1, True], [input2, button1_state], [input3, button2_state]]
        # 创建并启动搜索线程
        QtCore.QCoreApplication.processEvents()
        self.search_thread = SearchThread(search_list, self.get_path())
        self.search_thread.search_completed.connect(self.handle_search_completed)
        self.search_thread.start()
        print('search')
        # 关闭进度对话框
        progress_dialog.close()
        print('dialog_close')

    def handle_search_completed(self, search_results):
        second_page = SecondPage(search_results)
        second_page.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        second_page.exec_()'''

    def generate_new_page(self):
        # 显示进度对话框
        self.progress_dialog = QProgressDialog("搜索中...", "", 0, 0, self)
        self.progress_dialog.setWindowTitle("处理中")
        self.progress_dialog.setFixedSize(400, 200)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.show()

        input1 = self.text_input1.text()
        input2 = self.text_input2.text()
        input3 = self.text_input3.text()
        if self.button1.text() == "AND":
            button1_state = True
        else:
            button1_state = False
        if self.button2.text() == "AND":
            button2_state = True
        else:
            button2_state = False
        search_list = [[input1, True], [input2, button1_state], [input3, button2_state]]
        # 启动搜索任务
        self.search_worker.keywords = search_list
        self.search_worker.folder_path = self.get_path()
        QThreadPool.globalInstance().start(self.search_worker)

    def handle_search_completed(self, search_results):
        # 关闭进度对话框
        self.progress_dialog.close()
        second_page = SecondPage(search_results)
        second_page.setWindowFlags(Qt.WindowStaysOnTopHint)
        second_page.exec_()

    def closeEvent(self, event):
        # 确保在关闭主窗口时停止搜索线程
        if self.search_thread is not None:
            self.search_thread.quit()
            self.search_thread.wait()
        event.accept()

    def toggle_button1(self):
        if self.button1.text() == "AND":
            self.button1.setText("NOT")
        else:
            self.button1.setText("AND")

    def toggle_button2(self):
        if self.button2.text() == "AND":
            self.button2.setText("NOT")
        else:
            self.button2.setText("AND")

class SecondPage(QDialog):
    def __init__(self, inputs):
        super().__init__()
        self.config = QSettings("config.ini", QSettings.IniFormat)
        folder_path = self.config.value("folder_path")
        self.setWindowTitle('搜索结果')
        self.setGeometry(100, 100, 1200, 900)
        self.file_results = inputs
        
        # 解析数据结构
        file_results = inputs  # 假设inputs为大列表
        
        # 创建主布局
        layout = QVBoxLayout()
        
        # 创建表格
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['文件名', '出现频次', '功能选项', '其它'])
        
        # 设置表格属性
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setColumnWidth(0, 700)
        
        # 遍历大列表并添加数据行
        for file_result in file_results:
            filename = file_result[0]
            details = file_result[2]
            frequency = len(details)
            file_path = folder_path + '\\' + filename
            
            # 创建表格行
            row = table.rowCount()
            table.insertRow(row)
            
            # 添加文件名
            filename_item = QTableWidgetItem(filename)
            filename_item.setFlags(filename_item.flags() | QtCore.Qt.ItemIsSelectable)  # 允许选择
            table.setItem(row, 0, filename_item)
            
            # 添加查询到的频次
            frequency_item = QTableWidgetItem(str(frequency))
            table.setItem(row, 1, frequency_item)
            
            # 添加展开按钮
            expand_button = QPushButton('展开')
            expand_button.clicked.connect(lambda checked, row=row: self.expand_details(row))  # 传递行索引
            table.setCellWidget(row, 2, expand_button)
            
            # 添加打开按钮
            open_button = QPushButton('打开')
            open_button.clicked.connect(partial(self.open_file, file_path))
            table.setCellWidget(row, 3, open_button)
        
        # 将表格添加到布局
        layout.addWidget(table)
        
        # 设置布局
        self.setLayout(layout)
    
    def expand_details(self, row):
        # 展开按钮点击事件的处理逻辑
        file_result = self.file_results[row]
        details = remove_duplicates(file_result[2])
        # 创建展开窗口
        expand_window = QDialog(self)
        expand_window.setWindowTitle('详细信息')
        
        # 创建文本浏览器
        text_browser = QTextBrowser(expand_window)
        text_browser.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse | QtCore.Qt.TextSelectableByKeyboard)  # 设置文本可以被选中和复制
        text_browser.setFixedSize(600, 800)  # 设置文本浏览器的固定大小
        # 添加关键语句和所在页码
        for detail in details:
            print(detail)
            page_num = detail[0]
            keywords = detail[1]
            statements = detail[2:]
            
            # 生成带有标红关键词的语句
            highlighted_statements = keywords
            statements = sort_list(statements)
            start_tag = f'<span style="color:red">'
            end_tag = '</span>'
            if len(statements) == 1:
                highlighted_statements = '...'+highlighted_statements[:statements[0][0]]+start_tag+highlighted_statements[statements[0][0]:statements[0][1]]+end_tag+highlighted_statements[statements[0][1]:]+'...'
                print(highlighted_statements)
            if len(statements) == 2:
                highlighted_statements = '...'+highlighted_statements[:statements[0][0]]+start_tag+highlighted_statements[statements[0][0]:statements[0][1]]+end_tag+highlighted_statements[statements[0][1]:statements[1][0]]+start_tag+highlighted_statements[statements[1][0]:statements[1][1]]+end_tag+highlighted_statements[statements[1][1]:]+'...'
                print(highlighted_statements)
            if len(statements) == 3:
                highlighted_statements = '...'+highlighted_statements[:statements[0][0]]+start_tag+highlighted_statements[statements[0][0]:statements[0][1]]+end_tag+highlighted_statements[statements[0][1]:statements[1][0]]+start_tag+highlighted_statements[statements[1][0]:statements[1][1]]+end_tag+highlighted_statements[statements[1][1]:statements[2][0]]+start_tag+highlighted_statements[statements[2][0]:statements[2][1]]+end_tag+highlighted_statements[statements[2][1]:]+'...'
                print(highlighted_statements)
            # 构建关键语句和所在页码的文本
            statements_str = highlighted_statements+'<br>'
            text_browser.append(f'所在页码：{page_num}')
            text_browser.append(f'语句：{statements_str}')
        
        # 设置展开窗口布局
        expand_layout = QVBoxLayout()
        expand_layout.addWidget(text_browser)
        expand_window.setLayout(expand_layout)
        
        # 显示展开窗口
        expand_window.exec_()
    
    def open_file(self, file_path):
        # 打开按钮点击事件的处理逻辑
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
    

def sort_list(lst):
    # 剔除第一项为-2的子列表
    lst = [sublist for sublist in lst if sublist[0] != -2]
    # 根据子列表的第一项大小进行排序
    sorted_lst = sorted(lst, key=lambda x: x[0])
    # 将每个子列表的第二项加上第一项
    for sublist in sorted_lst:
        sublist[1] += sublist[0]
    sublist = merge_intervals(sorted_lst)
    return sublist

def merge_intervals(intervals):
    if not intervals:
        return []
    
    merged_intervals = [intervals[0]]
    
    for interval in intervals[1:]:
        prev_interval = merged_intervals[-1]
        
        if interval[0] <= prev_interval[1]:
            prev_interval[1] = max(prev_interval[1], interval[1])
        else:
            merged_intervals.append(interval)
    
    return merged_intervals

def remove_duplicates(list_of_lists):
    unique_lists = []
    for sublist in list_of_lists:
        if sublist not in unique_lists:
            unique_lists.append(sublist)
    return unique_lists

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())