# Next Level 웹 사이트 만들기 프로젝트

![image](https://raw.githubusercontent.com/nextlevelproject/talentproject/main/talent/static/images/MainPage.png)

### INDEX
1. [프로젝트 소개](#1-프로젝트-소개)
2. [팀원 구성과 역할](#2-팀원-구성과-역할)
3. [개발 환경](#3-개발-환경)
4. [프로젝트 기획 및 설계](#4-프로젝트-기획-및-설계)  
5. [구현 기능](#5-구현-기능)
6. [느낀점](#6-느낀점)

<br>

## 1. 프로젝트 소개

### 재능판매 사이트
- 전문가들이 자신의 재능을 사업화하여 판매하고 소비자들이 구매합니다.
  ### 특징
  - 전문가로 로그인하시면 상점을 등록할 수 있고 회원과 전문가 모두 커뮤니티를 이용할 수 있습니다.
  - 카테고리별로 원하는 상품을 찾아 원하는 전문가를 찾을 수 있습니다.
<br>

## 2. 팀원 구성과 역할

<div align="center">

| **박선영** | **김금** | **이기화** | **정연덕** |
| :------: | :------: | :------: | :------: |
| [<img src="https://raw.githubusercontent.com/nextlevelproject/talentproject/main/talent/static/images/N.png" width="150" height="150"> <br/> @dny1010](https://github.com/dny1010) | [<img src="https://raw.githubusercontent.com/nextlevelproject/talentproject/main/talent/static/images/E.png" width="150" height="150"> <br/> @rlakeum93](https://github.com/rlakeum93) | [<img src="https://raw.githubusercontent.com/nextlevelproject/talentproject/main/talent/static/images/X.png" width="150" height="150"> <br/> @kendou11](https://github.com/kendou11) | [<img src="https://raw.githubusercontent.com/nextlevelproject/talentproject/main/talent/static/images/T.png" width="150" height="150"> <br/> @yeondeok96](https://github.com/yeondeok96) |
| Main Page <br> 상점 Page <br> 상점 등록, 수정 및 삭제 <br> DB 관리 <br> | Community Page <br> 커뮤니티 등록, 수정 및 삭제 <br> 커뮤니티 댓글 및 좋아요 | 로그인 <br> 일반, 전문가 회원가입 <br> ID, PW 찾기 | 고수찾기 Page


</div>

<br>

## 3. 개발 환경

**Back-End** 
<div>
<img src="https://img.shields.io/badge/Flask-181717?style=for-the-badge&logo=flask&logoColor=white">  
<img src="https://img.shields.io/badge/SQLite-4479A1?style=for-the-badge&logo=sqlite&logoColor=white">
</div>
<br>

**Front-End** 
<div>
<img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=HTML5&logoColor=fff"/>
<img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=CSS3&logoColor=fff"/>
<img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=JavaScript&logoColor=fff"/>
<img src="https://img.shields.io/badge/bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=fff"/>
<img src="https://img.shields.io/badge/fontawesome-3a3f5b?style=for-the-badge&logo=fontawesome&logoColor=white">
</div> 
<br>

**Tools** 
<div>
<img src="https://img.shields.io/badge/Docker-1572B6?style=for-the-badge&logo=docker&logoColor=white">
<img src="https://img.shields.io/badge/figma-adb5bd?style=for-the-badge&logo=Figma&logoColor=white">
<img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=GitHub&logoColor=white">
</div>
<br>

## 4. 프로젝트 기획 및 설계

#### 개발 기간

<details>
  <summary>전체 개발 기간 : 2025-09-22 ~ 2025-10-14</summary>
  ![image](https://github.com/ChunjaeMomCh/MomChannel/assets/40616792/c2b695a4-c8fe-425e-9a10-8558fd2e7f1b)
</details>

#### 프로젝트 구조
```text
talentproject/
├── talent/
│   ├── __init__.py 
│   ├── models.py                
│   ├── forms.py                
│   ├── filter.py                
│   ├── views/
│   │   ├── main_views.py        
│   │   ├── auth_views.py        
│   │   ├── store_views.py       
│   │   ├── community_views.py   
│   │   └── category_views.py    
│   ├── templates/               
│   └── static/                 
├── config.py                    
├── requirements.txt             
├── Dockerfile                   
└── README.md
```

#### UML 다이어그램 및 경로 설정
<details>
  
  <summary>Diagram</summary>
  <br>
  <summary>Use Case Diagram</summary>
  
  ![image](https://github.com/ChunjaeMomCh/MomChannel/assets/145963633/d143c9f2-23a2-4e43-8e5f-be24c2611a71)

<br>
  <summary>Class Diagram</summary>
  
  ![image](https://github.com/ChunjaeMomCh/MomChannel/assets/145963633/d143c9f2-23a2-4e43-8e5f-be24c2611a71)

</details>

<details>
  <summary>URL 경로</summary>
</details>


## 5. 구현 기능

### [ 공통 레이아웃 및 Header ]
- 모든 페이지에서 공통으로 사용하는 `base.html`, `navbar.html`, `footer.html` 구조를 분리하여 화면 레이아웃을 재사용했습니다.
- 상단 내비게이션에서 메인, 고수찾기, 스토어, 커뮤니티로 이동할 수 있습니다.
- 로그인 상태에 따라 메뉴 노출을 다르게 처리했습니다.
  - 비로그인 사용자: 로그인/회원가입 메뉴 제공
  - 로그인 사용자: 사용자 이름 표시, 마이페이지, 프로필 수정, 로그아웃 메뉴 제공
- Flask의 `g.user`와 로그인 세션 정보를 활용해 템플릿에서 현재 로그인 사용자를 판별하도록 구현했습니다.

| 비회원 |
| --- |
| ![image](https://raw.githubusercontent.com/nextlevelproject/talentproject/main/talent/static/images/nologin.png) | 

| 회원 |
| --- |
| ![image](https://raw.githubusercontent.com/nextlevelproject/talentproject/main/talent/static/images/login.png) |

<br>

### [ 메인 페이지 ]
- 서비스의 첫 화면으로 카테고리, 광고 배너, 인기 스토어, 인기 커뮤니티 게시글을 한 번에 볼 수 있도록 구성했습니다.
- Swiper 라이브러리를 활용해 카테고리 슬라이더, 광고 배너 슬라이더, 전문가 가입 유도 영역을 구현했습니다.
- 스토어와 커뮤니티 게시글은 조회수 & 좋아요 수와 등록일 기준으로 상위 3개를 노출합니다.

| 메인 페이지 |
| --- |
| ![image](https://raw.githubusercontent.com/nextlevelproject/talentproject/main/talent/static/images/main.png) |




<br>


### [ 회원가입 및 로그인 ]
- 일반 회원과 전문가 회원 가입을 분리해서 구현했습니다.
  - 일반 회원: 기본 사용자 정보 기반 가입
  - 전문가 회원: 제공 서비스, 활동 지역 정보를 추가로 입력
- 회원가입 시 아이디, 이메일, 전화번호 중복 여부를 DB에서 확인합니다.
- 비밀번호는 평문 저장 없이 Werkzeug의 `generate_password_hash`를 사용해 해시 값으로 저장합니다.
- 로그인 시 입력한 비밀번호를 `check_password_hash`로 검증합니다.
- 로그인 성공 시 세션에 사용자 ID와 전문가 여부를 저장해 권한 분기와 화면 표시에서 활용합니다.
- 아이디 찾기, 비밀번호 찾기, 비밀번호 재설정 기능을 제공하며, 비밀번호 재설정에는 JWT 토큰과 Flask-Mail 전송 흐름을 적용했습니다.
- 프로필 수정 페이지에서 이름, 이메일, 전화번호를 수정할 수 있습니다.
- 전문가 회원의 경우 서비스 분야와 활동 지역 정보도 함께 수정할 수 있습니다.

| 일반 회원가입 폼 | 전문가 회원가입 폼 |
| --- | --- |
| ![image](https://raw.githubusercontent.com/nextlevelproject/talentproject/main/talent/static/images/create.png) | 
![image](https://raw.githubusercontent.com/nextlevelproject/talentproject/main/talent/static/images/procreate.png) |

<br>
<br>

| 비밀번호 재설정 | 회원정보 관리 |
| --- | --- |
| ![image](https://raw.githubusercontent.com/nextlevelproject/talentproject/main/talent/static/images/newpassword.png) | 
![image](https://raw.githubusercontent.com/nextlevelproject/talentproject/main/talent/static/images/update.png) |

<br>

### [ 고수찾기 및 카테고리 ]
- 사용자가 원하는 생활 서비스를 찾을 수 있도록 카테고리별 페이지를 구성했습니다.
- 이사, 청소, 설치, 수리, 인테리어, 이벤트, 뷰티, 패션, 취업, 과외, 취미, 반려동물, 법률, 차량관리, 여행, 기타 카테고리를 제공합니다.
- 각 카테고리는 독립적인 Flask Blueprint 라우트와 템플릿으로 연결되어 있어 페이지 확장이 쉽도록 구성했습니다.
- 카테고리별 체크박스 폼을 WTForms 기반으로 구성해 사용자가 세부 서비스를 선택할 수 있도록 설계했습니다.

<br>

| 카테고리 상세 페이지 ||
| --- | --- |
| ![image](https://raw.githubusercontent.com/nextlevelproject/talentproject/main/talent/static/images/category_detail.png) |

<br>


<br>

### [ 스토어 페이지 ]
- 전문가 회원이 자신의 서비스를 상품처럼 등록할 수 있는 기능입니다.
- 스토어 목록에서는 최신순으로 상품을 확인할 수 있으며, 검색어 입력 시 상품 제목, 내용, 작성자 이름을 기준으로 검색됩니다.
- 스토어 상세 페이지 진입 시 조회수를 증가시켜 인기 상품 노출 기준으로 활용합니다.
- 상품 등록 시 제목, 내용, 가격, 이미지를 입력받고 상품 수정 시 기존 상품 정보를 불러오고 새 이미지를 등록하면 이미지 경로를 갱신합니다.
- 상품 수정과 삭제는 작성자 본인에게만 허용되도록 권한을 검증하고. 전문가 회원이 아닌 사용자가 상품 등록 페이지에 접근하면 목록 페이지로 이동시켜 권한 없는 등록을 방지했습니다.

| 상점페이지 | 상점 등록 페이지 |
| --- | --- |
| ![image](https://raw.githubusercontent.com/nextlevelproject/talentproject/main/talent/static/images/store.png) | 
![image](https://raw.githubusercontent.com/nextlevelproject/talentproject/main/talent/static/images/store_create.png) |


<br>


<br>

### [ 커뮤니티 페이지 ]
- 게시글 작성 시 제목, 내용, 카테고리, 전문가 표시 여부, 이미지를 함께 등록할 수 있습니다.
- 전체 게시글 목록과 카테고리별 게시글 목록을 제공하고 게시글 좋아요와 댓글 좋아요 기능을 구현했습니다.
- 게시글 상세 페이지에서 댓글을 작성할 수 있으며, 댓글은 작성자와 게시글을 연결해 DB에 저장합니다.
- 게시글과 댓글 삭제 시 작성자 권한을 확인해 본인이 작성한 데이터만 삭제할 수 있도록 처리했습니다.

| 커뮤니티 페이지 | 커뮤니티 상세페이지 |
| --- | --- |
| ![image](https://raw.githubusercontent.com/nextlevelproject/talentproject/main/talent/static/images/community.png) | 
![image](https://raw.githubusercontent.com/nextlevelproject/talentproject/main/talent/static/images/community_detail.png)

<br>


<br>

## 6. 느낀점

**N 박선영**: 이번 프로젝트를 통해 Flask의 구조와 웹 서비스의 동작방식을 처음 배웠습니다. 
Flask를 사용하면서 처음에는 로그인, 게시글 작성, 상점페이지 같은 기능을 개별로 만들었지만 나중에 이 기능들이 서로 연결되어 
하나의 사용자 흐름이 완성되는 과정을 보며 단순히 기능을 구현하는 것보다 페이지 간의 연결성과 데이터 흐름을 설계하는 것이 중요하다는 점을 느꼈습니다.
또한 첫 팀 프로젝트를 진행하며 기능 구현 뿐만 아니라 팀원들의 의지, 지속적인 소통, 책임감 있는 협업이 프로젝트 완성도에 큰 영향을 미친다는 점을 깨달을 수 있었습니다.
