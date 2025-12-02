# Evaluation Report: ERP System QA Dataset

**Generated:** 2025-12-02T10:58:15.517018
**Total Test Cases:** 26

## Aggregate Generation Metrics

| Metric | Value |
|--------|-------|
| mean_correctness | 1.3846 |
| mean_completeness | 1.3846 |
| mean_relevance | 2.3846 |
| mean_coherence | 3.4231 |
| mean_overall_score | 1.7308 |

## Individual Results Summary

| Test Case | Overall Score | Correctness | Completeness | Latency (ms) |
|-----------|---------------|-------------|--------------|--------------|
| it-001 | 2.0 | 1.0 | 1.0 | 8901.4 |
| it-002 | 3.0 | 3.0 | 3.0 | 3642.4 |
| it-003 | 2.0 | 2.0 | 2.0 | 3598.8 |
| it-004 | 1.0 | 1.0 | 1.0 | 3666.5 |
| it-005 | 1.0 | 1.0 | 1.0 | 3271.1 |
| it-006 | 2.0 | 1.0 | 1.0 | 3675.1 |
| v5-001 | 2.0 | 1.0 | 1.0 | 2735.8 |
| v5-002 | 2.0 | 1.0 | 1.0 | 2937.8 |
| v5-003 | 1.0 | 1.0 | 1.0 | 3001.2 |
| v5-004 | 1.0 | 1.0 | 1.0 | 2747.3 |
| v5-005 | 3.0 | 3.0 | 3.0 | 3656.7 |
| v5-006 | 3.0 | 3.0 | 3.0 | 3246.4 |
| v5-007 | 2.0 | 1.0 | 1.0 | 3103.2 |
| v5-008 | 2.0 | 1.0 | 1.0 | 3240.1 |
| prog-001 | 2.0 | 1.0 | 1.0 | 2996.4 |
| prog-002 | 1.0 | 1.0 | 1.0 | 3683.3 |
| prog-003 | 1.0 | 1.0 | 1.0 | 2995.6 |
| prog-004 | 2.0 | 2.0 | 2.0 | 3675.4 |
| prog-005 | 1.0 | 1.0 | 1.0 | 2793.6 |
| prog-006 | 2.0 | 2.0 | 2.0 | 3611.9 |
| prog-007 | 1.0 | 1.0 | 1.0 | 3285.5 |
| prog-008 | 2.0 | 1.0 | 1.0 | 2129.1 |
| prog-009 | 2.0 | 1.0 | 1.0 | 2110.7 |
| prog-010 | 1.0 | 1.0 | 1.0 | 1461.7 |
| prog-011 | 2.0 | 2.0 | 2.0 | 2741.7 |
| prog-012 | 1.0 | 1.0 | 1.0 | 2975.1 |

## Detailed Results

### it-001

**Question:** 如果訂單 cust po no 有錯誤，可以自己修改嗎？用哪支程式可以修改？

**Expected Answer:** 可以透過 DT201 做異動

**Generated Answer:** 根據提供的文件內容，**不可以自己修改訂單的 cust po no**。

文件中提到：
- 在「PO Status Inquiry」功能中，可以查詢 PO 狀態、價格、維護需求日期、ETD/ETA，但並未提及可以修改 PO 號碼。
- 在「Data Process > Search」功能中，可以查詢資料，但沒有提供修改功能。
- 在「RMA History」功能中，可以查詢 RMA 的歷史記錄，但沒有提供修改功能。

此外，文件中提到的「RMA Receive Report」、「RMA invoice」、「Receive Trace Report」等報告，都是用來查詢資料的，並沒有提供修改功能。

因此，根據文件內容，**訂單的 cust po no 是不能自己修改的**，需要由系統管理員或相關授權人員進行修改，但文件中並未提及具體的程式或功能可以修改此欄位。

**Reasoning:** The GENERATED ANSWER is incorrect as it states that the cust po no cannot be modified by the user, while the REFERENCE ANSWER indicates it can be modified using DT201. The GENERATED ANSWER does not cover the key point of the specific program (DT201) that allows modification, leading to low scores in correctness and completeness. The relevance is somewhat maintained as it discusses the modification of cust po no, but it diverges by focusing on the inability to modify. The coherence is relatively high as the answer is well-structured and easy to follow.

---

### it-002

**Question:** Qty Avail、Qty Allocate、Qty Onhand 這些欄位分別代表什麼意思？

**Expected Answer:** Qty Avail (即剩餘的庫存數) = Qty Onhand – Qty Allocate；Qty Allocate 是目前 Allocate 的數量；Qty Onhand 是原本的庫存數

**Generated Answer:** 根據提供的文件內容，雖然沒有明確的定義表格，但可以從上下文推斷出這些欄位的含義：

*   **Qty Avail (可用數量)**：這通常代表在庫的、可供銷售或使用的數量。它可能包含在庫數量，但不包括已分配或已預訂的數量。
*   **Qty Allocate (已分配數量)**：這代表已經被分配給特定客戶、項目或內部部門的數量。它通常是從總庫存中減去的。
*   **Qty Onhand (現有數量)**：這代表目前實際存放在倉庫中的數量。它是最基本的庫存數量，通常由系統自動計算，是其他欄位的基礎。

這些欄位在庫存管理中非常關鍵，用於追蹤和管理庫存的流動。在文件的第2頁，提到了「Inventory Transaction

**Reasoning:** The GENERATED ANSWER provides a general understanding of the terms but lacks the specific formula and relationships mentioned in the REFERENCE ANSWER. It correctly identifies the general meaning of each term but does not explicitly state that Qty Avail is calculated as Qty Onhand minus Qty Allocate. The answer is mostly relevant and coherent, but it misses key details about the relationships between the quantities, affecting correctness and completeness.

---

### it-003

**Question:** SO 無法存檔，出現 Schedule Forwarder To address is not defined 錯誤訊息，該怎麼處理？

**Expected Answer:** 進 FS019 找 SO 上的客戶資料，Ship to Add -> Forwarder 一定要有值，若沒有值請填入 None

**Generated Answer:** 根據您提供的圖片和內容，此錯誤訊息「Schedule Forwarder To address is not defined」並未在任何圖片或文字中直接提及。然而，從上下文推斷，此錯誤通常發生在「PO Schedule approve」或「PO Schedule maintain」等與訂單排程相關的模組中，而這些模組在您提供的圖片中並未直接展示。

在您提供的圖片中，有關於「PO Schedule approve」的說明（圖片 1），但沒有關於「Schedule Forwarder」的具體設定。因此，根據您提供的資訊，無法直接從圖片中找到解決此錯誤的方法。

不過，根據一般ERP系統的邏輯，此錯誤通常意味著系統找不到預設的「Schedule Forwarder」地址。解決方法通常包括：

1.  **檢查系統設定**：進入系統設定，確認「Schedule Forwarder」的地址是否已正確設定。
2.  **檢查使用者權限

**Reasoning:** The GENERATED ANSWER does not accurately address the specific solution provided in the REFERENCE ANSWER, which is to check the 'Ship to Add -> Forwarder' field in FS019 and ensure it has a value. Instead, it provides a general approach to checking system settings and user permissions, which is not mentioned in the REFERENCE ANSWER. The GENERATED ANSWER is somewhat relevant as it discusses potential causes and solutions for the error, but it lacks the specific instruction given in the REFERENCE ANSWER. The coherence is moderate as the answer is understandable but not well-aligned with the specific question context.

---

### it-004

**Question:** 我有兩張 shipment no，可是卻無法合併成一張 packing，為什麼？

**Expected Answer:** 請檢查以下欄位值必須相同：oecust_br、oecust_dropship、currency、forwarder、importer、shipvia、shipping_term、shippoint_from、shippoint_to、shippoint_from_city、shippoint_to_city、ship_to、bill_to、sold_to、ship_priority、stat_edi、hold_user、territory

**Generated Answer:** 根據您提供的文件內容，這份文件主要介紹的是 **查詢（Query）** 和 **篩選（Filter）** 的操作方法，例如：
- 使用「like」關鍵字進行條件查詢（如 `like 1100001867% and like %BCM4708COKFEBG%`）。
- 使用「Search」功能（按 `Ctrl + F`）。
- 使用「Simple filter」功能（點擊欄位右鍵選擇）。

**文件中完全沒有提及任何關於「shipment no」、「packing」或「合併」的內容。**

因此，根據您提供的文件，**無法為您解答為什麼無法合併 shipment no 成一張 packing**。這可能與您使用的系統功能、操作流程或權限有關，但這些內容並未包含在您提供的文件中。建議您查詢系統的「Shipping」或「Packing」相關

**Reasoning:** The generated answer does not address the question about why two shipment numbers cannot be merged into one packing. It instead discusses query and filter operations, which are irrelevant to the question. The answer is coherent in its structure but completely incorrect and incomplete in terms of content relevance and accuracy.

---

### it-005

**Question:** DT092 unclose 選好 facility 卻找不到想看的單據，可能是什麼原因？

**Expected Answer:** 請確認 facility 是否設定會產生 packing no，且 Doc. Status 需符合以下條件：status_document < 70，包含 0 (New open)、2 (Pending By User)、10 (Doc Ready)、11 (Waiting Feed Back)、12 (Waiting for B2B Feed Back)、15 (Ask for Process)、20 (Process Ready)

**Generated Answer:** 根據提供的文件內容，DT092 選好 facility 卻找不到想看的單據，最可能的原因是 **該單據的 facility 欄位值與所選 facility 不匹配**。

文件第一頁的「Search & filter 二者差異如下」部分明確說明：
- **Search**：是針對 query 出來的**所有欄位**資料做 search（即全表搜尋）。
- **Filter**：是針對**單一欄位**做 search（即篩選特定欄位的值）。

在第二頁的「Query 方式介紹」中，也提到「用金手指查資料」時，需要「輸入在同一行，表示二者條件都要成立」，例如 `like 1100001867% and like %BCM4708COKFEBG%`，這表示搜尋條件是跨欄位的。



**Reasoning:** The generated answer does not address the specific reasons mentioned in the reference answer, such as checking if the facility is set to generate a packing number and ensuring the document status is less than 70. Instead, it discusses search and filter functionalities, which are not relevant to the question. The coherence is slightly better as the answer is structured and understandable, but it fails to provide the correct and complete information needed to answer the question.

---

### it-006

**Question:** DT092 不小心把 carton data 刪掉，要怎麼還原？

**Expected Answer:** 步驟：(1) 先切到 packing 頁籤，把 packing_no query 出來 (2) 把 packing detail 的 data 按右鍵 delete，切到 shipment list 頁籤 (3) 將 shipment no 或 packing no query 出來 (4) 按右鍵 Add shipment to current packing，再切到 carton list 頁籤就會產生新的

**Generated Answer:** 根據您提供的文件內容，**無法還原被刪除的 carton data**。

原因如下：
1.  **文件內容不包含相關資訊**：您提供的三張圖片（第0、1、2頁）僅說明了如何在「Item Master」中使用「Search」和「Filter」功能，並沒有提及任何關於「carton data」的儲存、恢復或備份機制。
2.  **無備份或恢復步驟**：文件中沒有任何關於「DT092」這個編號的資訊，也沒有說明如何恢復被刪除的資料。通常，若系統有備份功能，會在操作前提示或在系統設定中提供恢復選項，但這些資訊在文件中均未出現。
3.  **功能範圍不適用**：文件中的「Search」和「Filter」功能是用於篩選和查詢現有資料，

**Reasoning:** The generated answer is incorrect as it states that the carton data cannot be restored, which contradicts the reference answer that provides a step-by-step restoration process. It lacks completeness as it does not cover any of the key steps mentioned in the reference. The relevance is low because it does not address the specific question about restoring carton data, instead focusing on unrelated document content. The coherence is relatively high as the answer is well-structured and easy to follow, despite being incorrect.

---

### v5-001

**Question:** V5 地球上的 toolbar 圖示可以改小嗎？

**Expected Answer:** 在 User Info 不勾選「小圖示」，改完存檔後要關閉 V5 重開才會生效

**Generated Answer:** 根據提供的三張圖片，這些都是電腦螢幕截圖，顯示的是企業資源規劃（ERP）系統的介面，例如 CBN ACCMIS 和 Arcadyan ARCIMS。這些截圖中並未顯示任何關於「V5 地球」或其 toolbar 圖示可否縮小的資訊。此外，這些截圖中的介面元素（如按鈕、選單、表格）是固定尺寸的，並無提供調整大小的選項。因此，無法從提供的資料中確認「V5 地球上的 toolbar 圖示可以改小嗎？」這個問題的正確答案。

**Reasoning:** The generated answer does not address the question about changing the toolbar icon size in V5. It incorrectly focuses on unrelated screenshots and does not mention the necessary steps to change the icon size as described in the reference answer. The relevance is low because it does not directly address the question, and the coherence is slightly better as the response is understandable but not relevant.

---

### v5-002

**Question:** V5 地球登入的 format 可以調整嗎？

**Expected Answer:** 可以在 System style (系統樣式) 自己選擇要的 format

**Generated Answer:** 根據提供的文件內容，並未提及任何關於「V5 地球登入的 format 可以調整嗎？」的資訊。

文件中主要討論的是以下幾個主題：
- DT022：關於 Order Ack、Confirm Ship、以及 Ship 欄位的設定問題。
- DT009：關於 shipment 可合併條件及存檔時出現的錯誤訊息。
- 以及一些系統操作步驟，例如在 Item Master 中使用 Search 功能。

這些內容均與「V5 地球登入的 format」無關，文件中也沒有提供任何關於此項設定或調整的說明。

因此，根據目前提供的資料，無法回答這個問題。

**Reasoning:** The GENERATED ANSWER is incorrect as it states that the document does not provide information on adjusting the format for 'V5 地球登入', while the REFERENCE ANSWER clearly states that it can be adjusted in 'System style'. The GENERATED ANSWER is missing all key points from the REFERENCE ANSWER, leading to low completeness. It is somewhat relevant as it attempts to address the question but ultimately fails to provide the correct information. The coherence is moderate as the answer is structured and understandable, but it does not provide the necessary information.

---

### v5-003

**Question:** Fill Down Current Column 要怎麼用？

**Expected Answer:** 首先把要改的資料改好，按住 Shift 把要改的資料全選起來，滑鼠點在最後一筆，按右鍵選擇 Fill Down Current Column

**Generated Answer:** 在您提供的圖片中，並**沒有**顯示「Fill Down Current Column」這個功能或按鈕。這表示：

---

### ❗️「Fill Down Current Column」並非您圖片中顯示的選項

您圖片中顯示的是：

- 「Filter Editor」（過濾條件）
- 「Sort Ascending / Descending」
- 「Group By This Column」
- 「Show Group Panel」
- 「Filter Editor...」（被紅框標示）
- 以及「Part No」欄位的過濾條件設定（如 `Part No is like %A`）

---

## ✅ 「Fill Down Current Column」是什麼？

「Fill Down Current Column」（或稱「下拉填充」、「向下填充當前欄位」）是 Excel 或某些資料表軟體（如 SAP、Oracle、某些 ERP 系統）中常用的功能，用於：

> **將當前欄位中

**Reasoning:** The generated answer does not address the question of how to use 'Fill Down Current Column' at all. Instead, it discusses the absence of this feature in a provided image and lists unrelated features. It fails to provide any steps or instructions related to the question, making it completely incorrect and irrelevant. The coherence is slightly better as the text is structured, but it is not relevant to the question.

---

### v5-004

**Question:** Import file 的用途是什麼？Append Data 和 Update Destination 有什麼差別？

**Expected Answer:** Append Data 是 insert 的概念，以地球畫面為主新增進來。Update Destination 是 update 的概念，以要 Import 的檔案為主。若 part no 勾選 key Match，表示以 part no 為主，檔案裡 part no 只能唯一不能重複，若重複則以地球上的排序順序更新（找第一筆去更新）

**Generated Answer:** 在数据集成或ETL（Extract, Transform, Load）工具中，如 **Alteryx**、**Informatica**、**Talend**、**Microsoft Power BI** 或 **Google Data Studio** 等，**Import File**、**Append Data** 和 **Update Destination** 是三种常见的数据操作方式，它们的用途和区别如下：

---

## ✅ 1. Import File（导入文件）

### 📌 用途：
将外部文件（如 CSV、Excel、JSON、TXT 等）中的数据**导入到目标系统或数据表中**，通常用于**首次加载数据**或**初始化数据仓库**。

### 🧩 特点：
- 一般用于**首次加载**或**清空后重新加载**数据。
- 通常会**覆盖目标表中的现有数据**（除非指定保留策略）。
- 适用于**数据源是文件**，且目标是数据库或

**Reasoning:** The GENERATED ANSWER does not address the specific question about the differences between 'Append Data' and 'Update Destination' as described in the REFERENCE ANSWER. It instead provides a general explanation of 'Import File' in the context of data integration tools, which is not relevant to the specific concepts of 'Append Data' and 'Update Destination' as defined in the reference. The answer is somewhat coherent but lacks the necessary details and relevance to the question asked.

---

### v5-005

**Question:** Search 和 Filter 有什麼差異？

**Expected Answer:** Search 是針對 query 出來的所有欄位資料做搜尋；Filter 過濾條件是針對單一欄位做搜尋

**Generated Answer:** 根據提供的文件內容，**Search（搜尋）** 和 **Filter（篩選）** 是兩個不同的功能，主要差異在於它們的運作方式和用途：

1.  **Search (搜尋)**：
    *   **運作方式**：通常是在一個欄位或整個資料表中，根據特定的關鍵字或條件進行全表搜尋。它會返回所有符合條件的記錄。
    *   **用途**：用於快速定位特定的資料。例如，在「Inventory Trans」的「Apply No」欄位中，輸入「A1000022」，系統會搜尋所有與此編號相關的記錄。
    *   **文件中例證**：在「Inventory Trans」的介面中，有「Retrieve」按鈕，其功能是根據輸入的「Apply No」來搜尋對應的資料。同時，文件中

**Reasoning:** The GENERATED ANSWER provides a detailed explanation of 'Search' but does not adequately address 'Filter' as described in the REFERENCE ANSWER. It partially captures the concept of 'Search' but introduces additional details not present in the reference. The explanation of 'Filter' is missing, which affects completeness and correctness. The answer is mostly relevant to the question and is coherent, but it lacks the necessary comparison to fully address the question.

---

### v5-006

**Question:** Search 的快速鍵是什麼？除了快速鍵還有什麼方式？

**Expected Answer:** 快速鍵是 Ctrl + F，會多一個 search 欄位。另外也可以按右鍵 -> Data Process -> Search

**Generated Answer:** 根據圖片 1 中的截圖，顯示了在「Shipping Process」模組的「Packing」選單中，有「Search」功能。其快捷鍵為 **Ctrl + F**。

此外，根據圖片 1 中的文字說明，除了使用快捷鍵，還有以下方式可以進行搜尋：
1.  在「Packing」選單中，點擊「Search」按鈕。
2.  在「Packing」選單中，點擊「View Packing」按鈕，然後在彈出的視窗中使用「Search」功能。

因此，搜尋的快速鍵是 **Ctrl + F**，除此之外，也可以透過點擊選單中的「Search」按鈕或「View Packing」後的搜尋功能來進行。

**Reasoning:** The generated answer correctly identifies the shortcut key as Ctrl + F, which matches the reference. However, it introduces additional methods for searching that are not mentioned in the reference answer, such as clicking the 'Search' button or using 'View Packing'. This results in partial correctness and completeness. The relevance is mostly maintained as it addresses the question, but the extra details slightly deviate from the reference. The coherence is generally good, with a clear structure and logical flow.

---

### v5-007

**Question:** 如何取消 search？

**Expected Answer:** 直接按 X 關閉，或是把欄位內容清成空白

**Generated Answer:** 根据提供的文档内容，其中并未包含任何关于“如何取消 search”的说明或操作步骤。

文档主要围绕以下几个主题：
- DT011 和 DT136 的区别及操作（如删除 Apply No.）
- DT166 的 release 操作（如处理未知描述）
- DT185 的操作（如不做 picking）
- FT039 的操作（如维护客户信息、配置值）
- DT166 和 DT175 的 facility 选择逻辑
- 如何将两票 shipment 合并为一张 invoice

所有截图和文字描述均未提及任何与“取消搜索”（取消 search）相关的功能或操作方法。

因此，基于现有文档，无法提供“如何取消 search”的答案。

**Reasoning:** The GENERATED ANSWER does not provide the correct method to cancel a search as described in the REFERENCE ANSWER. It states that the document does not contain relevant information, which is incorrect according to the reference. The answer is mostly irrelevant to the question as it does not address the method of canceling a search. However, the answer is coherent and well-structured, making it easy to follow.

---

### v5-008

**Question:** Simple filter 在哪邊？

**Expected Answer:** 點選欄位，按右鍵 Data Process -> Simple filter

**Generated Answer:** 根據提供的圖片內容，並未顯示「Simple filter」這個功能或按鈕。

在第一張圖片中，展示了「AdmSlip Maintenance」和「AdmSlip Maintenance」的螢幕截圖，但沒有「Simple filter」的選項。在第二張圖片中，展示了「Shipping Transaction」和「Shipping List」的螢幕截圖，也沒有「Simple filter」的選項。在第三張圖片中，展示了「Normal Requisition」和「Customer Maintain」的螢幕截圖，同樣沒有「Simple filter」的選項。

因此，根據提供的資料，無法確定「Simple filter」在哪邊。可能這個功能並不存在於這些螢幕截圖中，或者它被隱藏在其他未顯示的選項中。

**Reasoning:** The GENERATED ANSWER does not provide the correct location of 'Simple filter' as described in the REFERENCE ANSWER. It fails to mention the process of right-clicking on a field and selecting 'Data Process -> Simple filter'. The answer is mostly irrelevant to the question as it focuses on the absence of 'Simple filter' in the images rather than addressing the question directly. The coherence is somewhat maintained as the answer is understandable, but it is not structured to address the question effectively.

---

### prog-001

**Question:** 開立 PR 是在哪支程式？

**Expected Answer:** DT073

**Generated Answer:** 根據提供的清單，**開立 PR（Purchase Requisition）** 的功能在 **「PR Entry · Create PR」** 這一行中明確列出。

這行的英文是：  
**PR Entry · Create PR**

---

✅ **答案：PR Entry · Create PR**

這表示在該系統中，開立採購申請（Purchase Requisition）的功能是透過 **PR Entry** 模組來執行，並稱為 **Create PR**。

---

📌 **補充說明**：  
在許多ERP系統（如SAP、Oracle、或自訂系統）中，「PR Entry」通常指「採購申請單」的建立功能，是採購流程的起點。此清單中也包含其他相關功能，如「RMA Order Entry」、「RTV purchase order」等，但「PR Entry」是專門用於開立 PR 的。

---

✅ 所以，**開立 PR 是

**Reasoning:** The GENERATED ANSWER is incorrect as it does not mention 'DT073', which is the correct answer according to the REFERENCE ANSWER. It instead provides information about 'PR Entry · Create PR', which is not relevant to the question. The answer is mostly irrelevant to the question asked, as it does not address the specific program 'DT073'. However, the answer is coherent and well-structured, making it easy to follow, but it fails to provide the correct and complete information required by the question.

---

### prog-002

**Question:** 開立 Purchase Order 是在哪支程式？

**Expected Answer:** DT007

**Generated Answer:** 根據提供的文件內容，開立 Purchase Order (PO) 的程式是 **PO change Buyer**。

在文件的第三頁（圖片 2）中，有一項明確列出：
- **PO change Buyer**：可針對單筆 po no 找出 buyer，或輸入 buyer 帶出名下所有 po no

雖然文件中未直接標示「開立 PO」的程式名稱，但「PO change Buyer」這個功能是針對已存在的 PO 進行修改買方的，這與開立新 PO 的操作是不同的。然而，在文件的第二頁（圖片 1）中，有提到「PO BILL，月結對帳單」，這暗示了與 PO 有關的其他功能。但根據文件內容，最直接與「開立 PO」相關的程式名稱並未明確列出，而是「PO change Buyer」。

此外，在文件的第二頁（圖片 1）中，

**Reasoning:** The generated answer incorrectly identifies 'PO change Buyer' as the program for opening a Purchase Order, while the reference answer specifies 'DT007'. The generated answer does not cover the key point from the reference answer and is mostly irrelevant to the question. The coherence is somewhat maintained, but the content is incorrect and incomplete, leading to a low overall score.

---

### prog-003

**Question:** 查詢 PR Report 是在哪支程式？

**Expected Answer:** DR075

**Generated Answer:** 根據提供的資料，**PR Report** 並未直接列出。然而，從上下文推斷，您可能是指 **PR Entry**（PR 記錄）或與之相關的 **PR Report**（PR 報表）。

在提供的清單中，有以下相關項目：

- **PR Entry · Create PR** → 這表示「PR 記錄」或「創建 PR」的功能。
- **PR Property Config** → 這表示「PR 屬性設定」，可能與 PR 報表相關。
- **Maintain Require** → 可能與 PR 有關的維護功能。
- **Vendor Contract Date Maintain** → 供應商合約日期維護，與 PR 有關。

但**沒有明確標示「PR Report」**的項目。

---

### 結論：

**根據提供的清單，並無「PR Report」的明確項目，

**Reasoning:** The generated answer is incorrect as it does not mention 'DR075', which is the correct answer. It is incomplete because it fails to provide the specific program where the PR Report is located. The relevance is low because it does not directly address the question, instead providing unrelated information about other programs. The coherence is somewhat understandable, but the structure is not directly answering the question, leading to a low overall score.

---

### prog-004

**Question:** 查詢 PO status、PO up 相關資訊是在哪支程式？

**Expected Answer:** DR007

**Generated Answer:** 根據提供的資料，在第一張圖片的「功能說明」部分，有提到「PO Status Inquiry · po status · price · Maintain Need Date, ETD,ETA 功能」，這表示 PO status 的查詢功能是透過「PO Status Inquiry」這個功能來進行的。

然而，這張圖片並未明確指出這個功能是在哪支程式中實現的。但根據上下文和常見的企業系統架構，這類功能通常會在「CBN ACCMIS V3」或類似的供應鏈管理系統中實現。此外，在第二張圖片中，我們可以看到「CBN ACCMIS V3 System」的螢幕截圖，這暗示了該系統是處理 PO 相關資訊的主系統。

綜合來看，雖然資料中沒有明確標示「PO Status Inquiry」功能是在哪支程式中，但根據螢幕截圖和功能描述，最有可能的程式是「

**Reasoning:** The generated answer does not correctly identify the specific program 'DR007' as the reference answer does. It speculates on possible systems without providing a definitive answer, which affects correctness and completeness. The relevance is somewhat maintained as it discusses related systems and functions, but it does not directly answer the question. The coherence is moderate, as the answer is understandable but lacks a clear conclusion. Overall, the generated answer fails to provide the precise information required by the question.

---

### prog-005

**Question:** 開立請領/入庫單要去哪支程式？

**Expected Answer:** DT011

**Generated Answer:** 根據提供的文件內容，開立請領/入庫單的程式是 **Inventory Transaction - Picking**。

在第一張圖片中，有一行文字明確提到：
**Inventory Transaction - Picking**，並附註說明「當做了DT141 pick時，allocatet資料就會被搬走」。

這表示「Inventory Transaction - Picking」是處理請領/入庫單的程式。此外，第二張圖片中也顯示了「Inventory Transaction - Picking」的選項，進一步佐證了其功能。

因此，開立請領/入庫單應使用 **Inventory Transaction - Picking** 程式。

**Reasoning:** The generated answer is incorrect as it identifies the wrong program ('Inventory Transaction - Picking') instead of the correct one ('DT011') for opening a requisition/receipt order. It does not cover any key points from the reference answer, which is simply the correct program code. While the answer is somewhat relevant to the question, it ultimately provides incorrect information. The coherence is relatively high as the answer is well-structured and easy to follow, but this does not compensate for the incorrectness and lack of completeness.

---

### prog-006

**Question:** 請領/入庫單扣帳是在哪支程式執行？

**Expected Answer:** DT012

**Generated Answer:** 根據提供的三張圖片內容，並未直接提及「請領/入庫單扣帳」這個具體操作的執行程式。

然而，我們可以從上下文推斷：
- 第一張圖片列出了「Inventory Transaction - Picking」，這代表了從倉庫取出貨品的流程，通常與「請領」相關。
- 第二張圖片討論了「DT022」的「Order Ack」與「Ship」，這與訂單確認和發貨有關，而「入庫單」通常是在發貨後才會產生。
- 第三張圖片則是關於「Clear Filter」的說明，與扣帳無關。

雖然「請領/入庫單扣帳」在這些圖片中沒有明確標示，但根據常見的ERP系統邏輯，「請領/入庫單扣帳」通常是在「Inventory Transaction」或「Stock Taking」等模組

**Reasoning:** The generated answer does not correctly identify the program 'DT012' as the one where '請領/入庫單扣帳' is executed, which is the key fact in the reference answer. It instead provides an analysis based on images that are not part of the reference answer, leading to incorrect conclusions. The answer is somewhat relevant as it attempts to address the question, but it fails to provide the correct and complete information. The coherence is relatively high as the answer is well-structured and easy to follow, but the lack of correct and complete information significantly impacts the overall score.

---

### prog-007

**Question:** 有程式可以 MRP 轉 PR 直接產生 PR 嗎？是哪支？

**Expected Answer:** DT016

**Generated Answer:** 根據提供的文件內容，**沒有提及任何可以「MRP 轉 PR 直接產生 PR」的程式或功能**。

文件第一頁列出的內容是各種系統操作與維護功能的清單，例如：
- Item Master (Footprint) - 原料進貨數量計算
- P/O Contract - 訂單制式貿易條款
- QVL Maintain - 固資自用折合
- PR Entry - Create PR
- Group Pick List
- Item Master Transaction (W/H Special Entry)

雖然清單中包含「PR Entry」這個項目，但這僅表示「可以建立 PR」，並未提及任何「自動化」或「由 MRP 觸發」的流程。文件中也沒有任何關於「MRP 轉 PR」自動化功能的說明。

此外，第二頁的內容是關於「Search & filter」的差異說明，與

**Reasoning:** The generated answer is incorrect as it states there is no program for MRP to PR conversion, while the reference answer clearly indicates 'DT016' as the program. The generated answer does not cover any key points from the reference answer, which is simply the program name. It is somewhat relevant as it discusses the topic of MRP to PR conversion, but it ultimately fails to provide the correct information. The coherence is moderate as the answer is structured and understandable, but it does not address the question correctly.

---

### prog-008

**Question:** 查詢供應商 EOL、COST/LT/MOQ/share rate maintain/last buy up/last receive up/buyer/sourcer 相關資料是在哪支程式？

**Expected Answer:** DT154

**Generated Answer:** 根據圖片一的內容，「供應商EOL,COST/LT/MOQ/share rate maintain/last buy up/last receive up/buyer/sourcer」相關資料的維護功能是在「Item Master Purchase Property Maintain」這個程式中進行的。這項功能位於圖片一的中段，與「Inventory StockRoom & Location」等其他維護功能並列。因此，相關資料維護的程式是「Item Master Purchase Property Maintain」。

**Reasoning:** The GENERATED ANSWER is incorrect as it provides a different program name ('Item Master Purchase Property Maintain') than the one specified in the REFERENCE ANSWER ('DT154'). It does not cover any key points from the reference answer, which is simply the program name. The relevance is low because the answer does not directly address the question with the correct program name, though it attempts to provide related information. The coherence is relatively high as the answer is well-structured and easy to follow, but it is ultimately incorrect and incomplete.

---

### prog-009

**Question:** Price Book (PO) maintain 是在哪支程式？

**Expected Answer:** DT157

**Generated Answer:** 根據提供的資料，並未明確指出「Price Book (PO) maintain」是哪支程式。在第0頁的列表中，有「Price Book (PO)」這個項目，但沒有標註其對應的程式名稱。同樣地，第1頁和第2頁也沒有提及這個項目與特定程式的關聯。因此，根據現有資訊，無法確定「Price Book (PO) maintain」是哪支程式。

**Reasoning:** The generated answer is incorrect as it fails to identify 'DT157' as the program for 'Price Book (PO) maintain'. It does not cover any key points from the reference answer, which is simply the program name. The relevance is somewhat maintained as it discusses the topic but fails to provide the correct information. The coherence is relatively high as the answer is clear and well-structured, but it ultimately does not provide the correct or complete information needed.

---

### prog-010

**Question:** SO Price book maintain 是在哪支程式？

**Expected Answer:** DT139

**Generated Answer:** 根據圖片二的內容，「SO Price book maintain」這個項目在「Price Book (PO)」的下方，屬於「Global PO Price Book maintain」的相關功能。因此，它是在「Global PO Price Book maintain」這個程式中進行維護的。

**Reasoning:** The GENERATED ANSWER is incorrect as it does not mention 'DT139', which is the correct program for 'SO Price book maintain'. It provides an incorrect program name and context, making it mostly irrelevant to the question. The answer is somewhat coherent, but it fails to address the correct information, leading to low scores in correctness, completeness, and relevance.

---

### prog-011

**Question:** 哪支程式可以查詢 part no 在各個庫的庫存？

**Expected Answer:** DR004

**Generated Answer:** 要查詢「Part No」在各個庫存（庫存庫）的現有數量，通常需要使用 **企業資源規劃（ERP）系統** 或 **庫存管理系統（Inventory Management System）**，這些系統會整合各個倉庫的數據，並提供查詢功能。

以下是常見的程式或系統，可用來查詢 Part No 在各庫存的庫存：

---

## ✅ 1. **ERP 系統（最常見）**

### 常見 ERP 系統：
- **SAP ERP**  
  → 使用「Inventory Management」模組，可查詢「Material Master」與「Stock Overview」，支援多倉庫查詢。
  → 用語：`Material Number` 或 `Part No`，查詢 `Stock Location` 或 `Warehouse`。

- **Oracle NetSuite / Oracle ERP Cloud**  
  → 提供「Inventory」→「Items」→「Stock

**Reasoning:** The GENERATED ANSWER does not mention the specific program 'DR004' as stated in the REFERENCE ANSWER, which is crucial for correctness and completeness. It instead provides a general explanation about ERP and inventory management systems, which is somewhat relevant but not directly answering the question. The coherence is relatively high as the answer is well-structured and easy to follow, but it lacks the specific information required by the question.

---

### prog-012

**Question:** 哪支程式可以查詢料號在所有倉的交易記錄或單據異動？

**Expected Answer:** DR005

**Generated Answer:** 根據提供的文件內容，**沒有明確提到任何程式或功能可以直接查詢料號在所有倉庫的交易記錄或單據異動**。

文件內容主要涵蓋的是：

- DT022（Order Ack）的資料要求與注意事項
- confirm ship 的操作與相關設定（如 DT201 修改客戶資料）
- 在 keyin so sent B2B 時 Ship 欄位的設定與 shipment no 的問題
- Qty Avail、Qty Allocate、Qty Onhand 的欄位說明
- Schedule Forwarder To address 未定義時的錯誤處理
- price hold 不走 e-approve 的設定（需改 AUTOAPPR）
- 什麼條件下會出現 Allocate Virtual（如 AT009、CT003、part no 屬性等）
- Schedule Forwarder To address not defined 的錯誤

**重點是：文件中沒有提及任何「查詢料號在

**Reasoning:** The generated answer is incorrect as it states that there is no program mentioned for querying transaction records, while the reference answer clearly states 'DR005' as the program. The generated answer does not cover any key points from the reference answer, making it incomplete. It is somewhat relevant as it attempts to address the question but ultimately fails to provide the correct information. The coherence is moderate as the answer is structured but does not provide the necessary information. Overall, the generated answer fails to meet the requirements of the question.

---
