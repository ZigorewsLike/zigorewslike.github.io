new Vue({
    el: '#app',
    data(){
        return{
            themeMode: "light_mode",
            publications: [
                {
                    title: "On automated workflow for fine-tuning deepneural network models for table detection in document images",
                    authors: "Igor Cherepanov, Andrey Mikhailov, Alexey Shigarov, and Viacheslav Paramonov",
                    conf: "2020 43rd International Convention on Information, Communication and Electronic Technology, MIPRO 2020 - Proceedings, 2020, pages 1130–1133, 9245241",
                    abstract: {
                        show: false,
                        text: "Nowadays methods and software for extracting tables from document images and portable documents (PDF) continue to be actively developed. One of the promising approaches to this task is the usage of fine-tuned object detection models. However, this approach involves many manipulations with data preparation and training process configuration. This paper proposes an automated workflow for fine-tuning deep neural network models for the table detection in document images. It enables us to automate two sub-tasks: (i) preparing a training dataset in the PascalVOC format with image transformation and augmentation; (ii) training a table detection model by using the well-known Faster R-CNN architecture. Implementation of the workflow design simplifies the use of the approach proposed by decreasing the number of required manipulations.",
                    },
                    citation: {
                        show: false,
                        text: "@INPROCEEDINGS{9245241,  author={I. {Cherepanov} and A. {Mikhailov} and A. {Shigarov} and V. {Paramonov}},  booktitle={2020 43rd International Convention on Information, Communication and Electronic Technology (MIPRO)},   title={On automated workflow for fine-tuning deepneural network models for table detection in document images},   year={2020},  volume={},  number={},  pages={1130-1133},  doi={10.23919/MIPRO48935.2020.9245241}}"
                    },
                    link: {
                        exist: true,
                        link: "https://doi.org/10.23919/MIPRO48935.2020.9245241",
                    },
                },
                {
                    title: "On Graph-Based Verification for PDF Table Detection",
                    authors: "Andrey Mikhailov, Alexey Shigarov, Egor Rozhkov, and Igor Cherepanov",
                    conf: "2020 Ivannikov Ispras Open Conference (ISPRAS)",
                    abstract: {
                        show: false,
                        text: "Many non-editable documents are shared in PDF (Portable Document Format). They are typically not accompanied by tags for annotating the page layout, including table positions. One of the important challenges of the analysis and understanding of such documents is table detection. This paper outlines a novel two-phase approach to the table detection in untagged PDF documents. The first phase uses deep neural networks (DNN) to predict some table candidates. The second phase selects probable tables from the candidates by verifying their graph representation. We build a weighted directed graph from text blocks inside a predicted area of a table. A set of such graphs produced from the “ICDAR 2013 Table Competition” dataset allowed us to train a verification model based on the Random Forest technique. The empirical results for competitive dataset demonstrated high performance of our implementation of this approach. We showed that additional verification enables reduction of errors and improvement of results of the PDF table detection.",
                    },
                    citation: {
                        show: false,
                        text: "@INPROCEEDINGS{9394071, author={Mikhailov, Andrey and Shigarov, Alexey and Rozhkov, Egor and Cherepanov, Igor}, booktitle={2020 Ivannikov Ispras Open Conference (ISPRAS)},  title={On Graph-Based Verification for PDF Table Detection},  year={2020}, volume={}, number={}, pages={91-95}, doi={10.1109/ISPRAS51486.2020.00020}}"
                    },
                    link: {
                        exist: true,
                        link: "https://doi.org/10.1109/ISPRAS51486.2020.00020",
                    },
                },
                {
                    title: "Towards end-to-end transformation of arbitrary tables from untagged portable documents (PDF) to linked data",
                    authors: "Alexey Shigarov, Igor Cherepanov, Evgeniy Cherkashin, Nikita Dorodnykh, Vasiliy Khristyuk, Andrey Mikhailov , Viacheslav Paramonov, Egor Rozhkow, and Alexandr Yurin",
                    conf: "CEUR Workshop Proceedings, 2019, 2463, pages 1–12",
                    abstract: {
                        show: false,
                        text: "The paper is devoted to the problem of an end-to-end table transformation from untagged portable documents (PDF) to linked data. It covers the issues of the table extraction from documents, the reconstruction of logical table structure, the conceptualization of their natural-language content, and the linking of extracted data with external vocabularies. We consider some perspective approaches for the deeplearning-based table detection, heuristic-based table structure recognition, rule-based table analysis, and knowledge-based table interpretation. They can be used as a basis to develop a consistent solution for this problem. Our application experience confirms that such solutions are demanded for populating databases and generating ontologies with tabular data being extracted from weakly and semi-structured documents.",
                    },
                    citation: {
                        show: false,
                        text: "@INPROCEEDINGS{2463,  author={A. {Shigarov}, I. {Cherepanov}, E. {Cherkashin}, N. {Dorodnykh}, V. {Khristyuk}, A. {Mikhailov} , V. {Paramonov}, E. {Rozhkow}, and A. {Yurin}},  booktitle={CEUR-WS Proc.},   title={Towards end-to-end transformation of arbitrary tables from untagged portable documents (PDF) to linked data.},   year={2019},  volume={},  number={},   pages={1-12},  }"
                    },
                    link: {
                        exist: true,
                        link: "http://ceur-ws.org/Vol-2463/paper1.pdf",
                    },
                }
            ],
            projects:[
                {
                    name: "PhotoDraw",
                    develope_mode: true,
                    description: 'Фоторедактор на pyqt5 с аппаратным ускорением через <a href="https://www.khronos.org/opencl/">OpenCL</a> (Своя версия фотошопа). Позволяет открывать и редактировать большие изображения без потери качества. <br><br> Реализованно: <lu><li>Домашняя страница с последними файлами</li><li>Открытие изображения</li><li>Изменение яркости, контрастности и <a href="https://helpx.adobe.com/photoshop/using/levels-adjustment.html">уровней</a></li></lu>',
                    links: [
                        {
                            name: "GitHub",
                            link: "https://github.com/ZigorewsLike/PhotoDraw",
                        }
                    ],
                    tags: ["Python", "PyQt5", "OpenCL"],
                    video_logo: true,
                    logo: "github_rep/photo_draw/workflow.webm",
                    gif:{
                        anim: false,
                        path: "",
                        frame: "",
                    },
                    logo_width: "400px"
                },
                {
                    name: "Dl4td",
                    develope_mode: false,
                    tags: ["Python", "TensorFlow"],
                    description: '<b>Dl4td</b> is the control script that allow to automate data preparation process, namely datasets conversion, image conversion, data augmentation, creation of TF Records files. These scripts help to create DNN-models for table detection in image documents. They aim at reducing user efforts needed for DL preparation and configuration.',
                    links: [
                        {
                            name: "Paper",
                            link: "https://doi.org/10.23919/MIPRO48935.2020.9245241",
                        },
                        {
                            name: "Project (Google colab)",
                            link: "https://colab.research.google.com/drive/1TDoXxlxGhrbeZfkID5xK0DNK7ikicbZC",
                        },
                        {
                            name: "GitHub",
                            link: "https://github.com/tabbydoc/dl4td",
                        }
                    ],
                    logo: "github_rep/dl4td/tables.png",
                    gif:{
                        anim: false,
                        path: "",
                        frame: "",
                    },
                    logo_width: "400px"
                },
                {
                    name: "NoJpg",
                    develope_mode: false,
                    tags: ["Python", "TensorFlow", "DVS"],
                    description: 'Некоторые изображения в интернете сохранены с потерей качества. В таких изображениях градиент цветов становился грубым, а мелкие детали пропадали вовсе. Восстановить такие изображения методом эвристик очень сложно. Эвристикой можно восстановить плавность некоторых участков изображения, но тогда оно станет мыльным и изображение не будет детальным. <br><b>NoJpeg_gan</b> - это проект, который убирает сжатие с JPG фотографии с помощью обученной глубокой нейронной сети. За основу взята архитектура сети <a href="https://arxiv.org/abs/1611.07004">pix2pix</a> и расширена до приёма изображения размеров 512 на 512 пикселей.',
                    links: [
                        {
                            name: "GitHub",
                            link: "https://github.com/ZigorewsLike/noJpg_gan",
                        }
                    ],
                    logo: "github_rep/nojpeg/logo.png",
                    gif:{
                        anim: false,
                        path: "",
                        frame: "",
                    },
                    logo_width: "400px"
                },
                {
                    name: "Xml_generator_online",
                    develope_mode: false,
                    tags: ["Vue", "Django"],
                    description: '<b>Xml_generator_online</b> - это веб-приложения, которое принимает пользовательское изображение и даёт возможность пользователю выделять области интереса так, как ему нужно и с той точностью, которая необходима. После выделения областей веб-приложение генерирует и сохранять результат в виде XML файла на компьютер пользователя. Проект создан на языке python  с использованием Django.',
                    links: [
                        {
                            name: "GitHub",
                            link: "https://github.com/ZigorewsLike/xml_generator_online",
                        }
                    ],
                    logo: "github_rep/xml_gen_online/workflow.png",
                    gif:{
                        anim: true,
                        path: "github_rep/xml_gen_online/workflow.gif",
                        frame: "github_rep/xml_gen_online/workflow.png",
                    },
                    logo_width: "400px"
                },
                {
                    name: "Nasa_rover_photos",
                    develope_mode: false,
                    tags: ["Vue", "CreateJs"],
                    description: '<b>Nasa_rover_photos</b> - это веб-приложения, с помощью которого можно смотреть фотографию любого из 4 марсоходов на заданную дату. Получение изображений осуществляется через <a href=\"https://api.nasa.gov\">Nasa Api</a>. <br> На сайте нужно первым делом выбрать ровер, а при выборе даты запрос автоматически отправится и покажет фотографии при наличии.',
                    links: [
                        {
                            name: "Проект",
                            link: "https://zigorewslike.github.io/nasa_rover_photos/",
                        },
                        {
                            name: "GitHub",
                            link: "https://github.com/ZigorewsLike/nasa_rover_photos",
                        },
                        {
                            name: "Android",
                            link: "https://play.google.com/store/apps/details?id=com.intercoder.mynasarover",
                        }
                    ],
                    logo: "github_rep/nasa_rover_web/logo.png",
                    gif:{
                        anim: false,
                        path: "",
                        frame: "",
                    },
                    logo_width: "400px"
                },
                {
                    name: "Cuda_convolution_image",
                    develope_mode: false,
                    tags: ["C#", "Cuda"],
                    description: '<b>Cuda_convolution_image</b> - это C# проект с пользовательским интерфейсом, который применяет матрицу свёртки к загруженному изображению. Все вычисления (применение свёртки) происходят на видеокарте от компании <u>Nvidia</u>. Проект загружает Cuda ядро, которое скомпилировано в dll файл. <br> Доступные размеры от 3 до 9 (нечётные значения)',
                    links: [
                        {
                            name: "GitHub",
                            link: "https://github.com/ZigorewsLike/cuda_convolution_image",
                        }
                    ],
                    logo: "github_rep/cuda_conv/workflow.png",
                    gif:{
                        anim: true,
                        path: "github_rep/cuda_conv/workflow.gif",
                        frame: "github_rep/cuda_conv/workflow.png",
                    },
                    logo_width: "400px"
                },
            ]
        }
    },
    created: function(){
        if(this.themeMode == "dark_mode"){
            document.body.setAttribute('style', '');
        }else{
            document.body.setAttribute('style', 'background-color: #161b1f; color: rgba(255, 255, 255, 0.86);');
        }
    },
    updated: function () {
        
              
    },
    methods: {
        publAbstractShow(index){
            for(let i=0;i<this.publications.length;i++){
                this.publications[i].citation.show = false;
                if(i != index)
                    this.publications[i].abstract.show = false;
            }
            this.publications[index].abstract.show = !this.publications[index].abstract.show;
        },
        publCitationShow(index){
            for(let i=0;i<this.publications.length;i++){
                this.publications[i].abstract.show = false;
                if(i != index)
                    this.publications[i].citation.show = false;
            }
            this.publications[index].citation.show = !this.publications[index].citation.show;
        },
        gifPlay(index){
            if(this.projects[index].gif.anim){
                this.projects[index].logo = this.projects[index].gif.path;
            }
        },
        gifStop(index){
            if(this.projects[index].gif.anim){
                this.projects[index].logo = this.projects[index].gif.frame;
            }
        },
        switchMode(){
            if(this.themeMode == "dark_mode"){
                this.themeMode = "light_mode";
                document.body.setAttribute('style', 'background-color: #161b1f; color: rgba(255, 255, 255, 0.86);');
            }else{
                this.themeMode = "dark_mode";
                document.body.setAttribute('style', '');
            }
        }
    }
});